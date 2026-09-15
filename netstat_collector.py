#!/usr/bin/env python3
"""
Netstat collector.

Every 5 minutes, POST a Grafana Elasticsearch data-source query to
https://monit-grafana-open.cern.ch/api/ds/query, rename each record's
fields, print one line per record, and index the result into the UC
Elasticsearch cluster (index "wlcg-sitenetwork-%Y.%m", document id taken
from the record's own "_id" so an overlapping fetch window updates rather
than duplicates):

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
    python netstat_collector.py           # run forever, polling every 5 min
    python netstat_collector.py --once    # fetch a single batch and exit
"""

import argparse
import copy
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ENDPOINT = "https://monit-grafana-open.cern.ch/api/ds/query?ds_type=elasticsearch&requestId=SQR103"
TEMPLATE_PATH = Path(__file__).with_name("request_data.json")

POLL_INTERVAL_SECONDS = 5 * 60
# Look back a bit further than the poll interval so a slow tick never
# leaves a gap between consecutive windows.
LOOKBACK_MINUTES = 6

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
# Column order for the printed, tab-separated log line.
OUTPUT_ORDER = ["_id", "timestamp", "netsite", "site",
                "InBytesPerSecond", "OutBytesPerSecond"]

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


def build_payload(template: dict) -> dict:
    """Return a copy of the template with a fresh from/to time window."""
    payload = copy.deepcopy(template)
    now_ms = int(time.time() * 1000)
    payload["to"] = str(now_ms)
    payload["from"] = str(now_ms - LOOKBACK_MINUTES * 60 * 1000)
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


def format_record(doc: dict) -> str:
    values = [doc.get(f) for f in OUTPUT_ORDER]
    return "\t".join("" if v is None else str(v) for v in values)


def es_index_name() -> str:
    return f"{ES_INDEX_PREFIX}-{datetime.now(timezone.utc):%Y.%m}"


def index_records(docs: list[dict]) -> None:
    """Bulk-index documents into the UC Elasticsearch cluster.

    Each document is indexed with its own "_id" as the document id, so
    re-fetching an overlapping time window overwrites rather than
    duplicates records. "_id" is a reserved metadata field name in
    Elasticsearch, so it's only used as the bulk action's document id, not
    stored inside the document source itself.
    """
    if not docs:
        return
    password = os.environ.get(ES_PASSWORD_ENV)
    if not password:
        print(f"{ES_PASSWORD_ENV} not set; skipping indexing", file=sys.stderr)
        return

    index = es_index_name()
    lines = []
    for doc in docs:
        action = {"index": {"_index": index}}
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
    if result.get("errors"):
        for item in result.get("items", []):
            info = item.get("index", {})
            if info.get("error"):
                print(
                    f"index error for _id={info.get('_id')}: {info['error']}",
                    file=sys.stderr,
                )


def run_once(template: dict) -> None:
    payload = build_payload(template)
    response = fetch(payload)
    docs = [transform_record(record) for record in extract_records(response)]
    for doc in docs:
        print(format_record(doc))
    index_records(docs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true",
                        help="fetch a single batch and exit")
    args = parser.parse_args()

    template = load_template()

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
