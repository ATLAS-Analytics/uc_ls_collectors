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

tr = {
    "result": {
        "paths": [
            [
                {"ip": "194.80.35.130", "number": 786, "rtt": "PT  0.2S"},
                {"ip": "194.80.37.225", "number": 786, "rtt": "PT 12.9S"},
                {"ip": "146.97.169.145", "number": 786, "rtt": "PT  0.8S"},
                {"ip": "146.97.78.69", "number": 786, "rtt": "PT  2.0S"},
                {"ip": "146.97.38.41", "number": 786, "rtt": "PT  1.9S"},
                {"ip": "146.97.33.41", "number": 786, "rtt": "PT  4.6S"},
                {"ip": "146.97.33.21", "number": 786, "rtt": "PT  7.4S"},
                {"ip": "146.97.41.34", "number": 786, "rtt": "PT  9.4S"},
                {"ip": "192.100.78.51", "number": 786, "rtt": "PT  9.3S"},
                {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {},
                {}, {}, {}, {}, {}, {}, {}
            ]
        ]
    },
    "test": {
        "spec": {
            "source": "pygrid-sonar1.lancs.ac.uk",
            "dest": "heplnx130.pp.rl.ac.uk",
            "ip-version": 4
        },
        "type": "trace"
    },
    "run": {
        "end-time": 1676469219000
    },
    "@timestamp": "2023-02-15T14:57:14Z",
    "id": "5e2b5b28-4538-49a4-abad-5517424404f",
    "push": False
}


def bulk_send(data):
    """
    sends the data to logstash.
    """
    for d in data:
        d['pull'] = True
        print(d)
        response = requests.put(
            "https://ps-collection.atlas-ml.org", json=d,
            timeout=20, verify=True, allow_redirects=True)
        print(response.status_code)
        if response.status_code != 200:
            print(f"ERROR: code {response.status_code}")


d = [th]

bulk_send(d)
