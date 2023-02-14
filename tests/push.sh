curl -X POST 'https://ps-collection.atlas-ml.org' --header 'Content-Type: application/json' --data '{
    "result": {
        "summary": {
            "summary": {"throughput-bytes": 7065349548.0, "retransmits": 16267.0}
        }
    }, 
    "test": {
        "spec": {
            "source": "2001:630:3c1:638::d545", 
            "dest": "2001:630:e4:2810:137:222:79:1", 
            "ip-version": 4
        }, 
        "type": "throughput"
    }, 
    "run": {
        "end-time": 1676393173000
        }, 
    "@timestamp": "2023-02-14T18:34:23Z", 
    "id": "5a7d2e40-019c-48da-957f-77a5572d043", 
    "push": "false"
    }'