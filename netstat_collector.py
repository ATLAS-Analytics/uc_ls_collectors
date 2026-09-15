#!/usr/bin/env python3
"""
Netstat collector.

Every 5 minutes, POST a Grafana Elasticsearch data-source query to
https://monit-grafana-open.cern.ch/api/ds/query, rename each record's
fields, and index the result into the UC Elasticsearch cluster (index
"wlcg-sitenetwork-%Y.%m", named after each record's own timestamp rather
than the current time; document id taken from the record's own "_id" so
an overlapping fetch window updates rather than duplicates). Each run
prints a one-line summary of how many docs were fetched/indexed, not the
documents themselves:

    _id                    -> _id
    metadata.timestamp     -> timestamp
    data.netsite           -> netsite
    data.site              -> site
    data.InBytesPerSec     -> InBytesPerSecond
    data.OutBytesPerSec    -> OutBytesPerSecond

The query template (query string, metrics, datasource, ...) is read from
request_data.json; only the "from"/"to" time window is recomputed on every
run so it always covers the last few minutes.

Indexing requires the LOGSTASH_PWD environment variable (password for the
uc_logstash_indexer user on atlas-kibana.mwt2.org); if it isn't set,
indexing is skipped and records are only printed.

Usage:
    python netstat_collector.py                        # run forever, polling every 5 min
    python netstat_collector.py --once                  # fetch a single batch and exit
    python netstat_collector.py --start ... --end ...   # interactive backfill of a date range
"""

import argparse
import copy
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ENDPOINT = "https://monit-grafana-open.cern.ch/api/ds/query?ds_type=elasticsearch&requestId=SQR103"
TEMPLATE_PATH = Path(__file__).with_name("request_data.json")

POLL_INTERVAL_SECONDS = 5 * 60
# Look back a bit further than the poll interval so a slow tick never
# leaves a gap between consecutive windows.
LOOKBACK_MINUTES = 6

# Chunk size used when backfilling an interactively-specified date range, so
# a long range is fetched (and indexed) as a series of smaller queries
# rather than one huge one.
BACKFILL_CHUNK_MINUTES = 60

# Raw field name (as returned by the Grafana ES datasource) -> renamed field
# used both for the printed output and for the indexed document.
RENAME = {
    "_id": "_id",
    "metadata.timestamp": "timestamp",
    "data.netsite": "netsite",
    "data.site": "site",
    "data.InBytesPerSec": "InBytesPerSecond",
    "data.OutBytesPerSec": "OutBytesPerSecond",
}
FIELDS = list(RENAME)

# Where/how to index, mirroring the elasticsearch output of the netstat
# Logstash pipeline (configs/netstat.conf).
ES_HOST = "atlas-kibana.mwt2.org"
ES_PORT = 9200
ES_INDEX_PREFIX = "wlcg-sitenetwork"
ES_USER = "uc_logstash_indexer"
ES_PASSWORD_ENV = "LOGSTASH_PWD"


def load_template() -> dict:
    with TEMPLATE_PATH.open() as f:
        return json.load(f)


def build_payload(template: dict, from_ms: int | None = None, to_ms: int | None = None) -> dict:
    """Return a copy of the template with a from/to time window.

    By default the window covers the last LOOKBACK_MINUTES up to now; pass
    from_ms/to_ms explicitly (e.g. for an interactive backfill) to override it.
    """
    payload = copy.deepcopy(template)
    if to_ms is None:
        to_ms = int(time.time() * 1000)
    if from_ms is None:
        from_ms = to_ms - LOOKBACK_MINUTES * 60 * 1000
    payload["to"] = str(to_ms)
    payload["from"] = str(from_ms)
    return payload


def fetch(payload: dict) -> dict:
    resp = requests.post(
        ENDPOINT,
        headers={"Content-Type": "application/json",
                 "Accept": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def extract_records(response: dict) -> list[dict]:
    """Turn the Grafana columnar "frames" response into a list of row dicts."""
    records = []
    for result in response.get("results", {}).values():
        if result.get("error"):
            print(f"query error: {result['error']}", file=sys.stderr)
            continue
        for frame in result.get("frames", []):
            field_names = [f["name"] for f in frame["schema"]["fields"]]
            columns = frame["data"]["values"]
            indices = {name: field_names.index(
                name) for name in FIELDS if name in field_names}
            if not indices:
                continue
            num_rows = len(columns[indices[FIELDS[0]]]
                           ) if FIELDS[0] in indices else 0
            for row in range(num_rows):
                record = {name: columns[idx][row]
                          for name, idx in indices.items()}
                records.append(record)
    return records


def transform_record(record: dict) -> dict:
    """Rename a raw record's fields per RENAME and normalize its timestamp."""
    doc = {RENAME[name]: value for name,
           value in record.items() if name in RENAME}
    ts = doc.get("timestamp")
    if isinstance(ts, (int, float)):
        doc["timestamp"] = datetime.fromtimestamp(
            ts / 1000, tz=timezone.utc).isoformat()
    return doc


def es_index_name(doc: dict) -> str:
    """Index name for a document, based on its own "timestamp" field.

    Falls back to the current time if the document has no usable timestamp,
    so a malformed record still gets indexed somewhere.
    """
    ts = doc.get("timestamp")
    when = None
    if isinstance(ts, str):
        try:
            when = datetime.fromisoformat(ts)
        except ValueError:
            when = None
    if when is None:
        when = datetime.now(timezone.utc)
    return f"{ES_INDEX_PREFIX}-{when:%Y.%m}"


def index_records(docs: list[dict]) -> int:
    """Bulk-index documents into the UC Elasticsearch cluster.

    Each document is indexed with its own "_id" as the document id, so
    re-fetching an overlapping time window overwrites rather than
    duplicates records. "_id" is a reserved metadata field name in
    Elasticsearch, so it's only used as the bulk action's document id, not
    stored inside the document source itself. Documents are routed to the
    monthly index matching their own timestamp, not the current time, so a
    backfill correctly lands in past months' indices.

    Returns the number of documents actually indexed (0 if skipped).
    """
    if not docs:
        return 0
    password = os.environ.get(ES_PASSWORD_ENV)
    if not password:
        print(f"{ES_PASSWORD_ENV} not set; skipping indexing", file=sys.stderr)
        return 0

    lines = []
    for doc in docs:
        action = {"index": {"_index": es_index_name(doc)}}
        doc_id = doc.get("_id")
        if doc_id:
            action["index"]["_id"] = doc_id
        source = {k: v for k, v in doc.items() if k != "_id"}
        lines.append(json.dumps(action))
        lines.append(json.dumps(source))
    body = "\n".join(lines) + "\n"

    resp = requests.post(
        f"https://{ES_HOST}:{ES_PORT}/_bulk",
        auth=(ES_USER, password),
        headers={"Content-Type": "application/x-ndjson"},
        data=body.encode("utf-8"),
        timeout=60,
    )
    resp.raise_for_status()
    result = resp.json()
    errors = 0
    if result.get("errors"):
        for item in result.get("items", []):
            info = item.get("index", {})
            if info.get("error"):
                errors += 1
                print(
                    f"index error for _id={info.get('_id')}: {info['error']}",
                    file=sys.stderr,
                )
    return len(docs) - errors


def run_once(template: dict, from_ms: int | None = None, to_ms: int | None = None) -> None:
    payload = build_payload(template, from_ms=from_ms, to_ms=to_ms)
    response = fetch(payload)
    docs = [transform_record(record) for record in extract_records(response)]
    indexed = index_records(docs)
    print(f"fetched {len(docs)} docs, indexed {indexed}")


def parse_datetime(value: str) -> datetime:
    """Parse a --start/--end CLI value (ISO date or datetime) as UTC."""
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def run_range(template: dict, start: datetime, end: datetime) -> None:
    """Backfill every record between start and end (inclusive of start).

    Fetched in BACKFILL_CHUNK_MINUTES-sized windows so a long range is
    broken into a series of smaller queries instead of one huge one.
    """
    chunk = timedelta(minutes=BACKFILL_CHUNK_MINUTES)
    cur = start
    while cur < end:
        chunk_end = min(cur + chunk, end)
        run_once(
            template,
            from_ms=int(cur.timestamp() * 1000),
            to_ms=int(chunk_end.timestamp() * 1000),
        )
        cur = chunk_end


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true",
                        help="fetch a single batch and exit")
    parser.add_argument("--start", type=parse_datetime,
                        help="backfill start (ISO date/datetime, e.g. 2026-01-01); "
                             "requires --end, interactive use only")
    parser.add_argument("--end", type=parse_datetime,
                        help="backfill end (ISO date/datetime), exclusive; requires --start")
    args = parser.parse_args()

    if bool(args.start) != bool(args.end):
        parser.error("--start and --end must be given together")
    if args.start and args.start >= args.end:
        parser.error("--start must be before --end")

    template = load_template()

    if args.start and args.end:
        run_range(template, args.start, args.end)
        return

    if args.once:
        run_once(template)
        return

    while True:
        start = time.monotonic()
        try:
            run_once(template)
        except Exception as exc:  # keep polling even if one iteration fails
            print(f"error fetching netstat data: {exc}", file=sys.stderr)
        elapsed = time.monotonic() - start
        time.sleep(max(0.0, POLL_INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    main()
