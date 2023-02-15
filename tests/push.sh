curl -X POST 'https://ps-collection.atlas-ml.org' --header 'Content-Type: application/json' --data '{
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
    "id": "1234567892",
    "pull":true
}'