import requests

th = {
    "result": {
        "summary": {"summary": {"throughput-bytes": 7065349548.0, "retransmits": 16267.0}}
    },
    "test": {
        "spec": {
            "source": "gridpp-ps-band.ecdf.ed.ac.uk",
            "dest": "dice-io-37-00.acrc.bris.ac.uk",
            "ip-version": 4
        },
        "type": "throughput"
    },
    "run": {
        "end-time": 1676393173000
    },
    "@timestamp": "2023-02-14T18:34:23Z",
    "id": "1234567893"
}


def bulk_send(data):
    """
    sends the data to logstash.
    """
    for d in data:
        d['push'] = False
        print(d)
        response = requests.put(
            "https://ps-collection.atlas-ml.org", json=d,
            timeout=20, verify=True, allow_redirects=True)
        print(response.status_code)
        if response.status_code != 200:
            print(f"ERROR: code {response.status_code}")


d = [th]

bulk_send(d)
