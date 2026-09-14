# To Do

        {
            "refId": "C",
            "alias": "IN: Total",
            "query": "data.site: *",
            "timeField": "metadata.timestamp",
            "datasource": {
                "type": "elasticsearch",
                "uid": "s0TUbLzIz"
            },
            "datasourceId": 10526,
            "intervalMs": 60000,
            "metrics": [
                {
                    "id": "1",
                    "type": "sum",
                    "field": "data.InBytesPerSec",
                    "settings": {}
                }
            ],
            "bucketAggs": [
                {
                    "id": "2",
                    "type": "date_histogram",
                    "field": "metadata.timestamp",
                    "settings": {
                        "interval": "auto"
                    }
                }
            ]
        },
        {
            "refId": "D",
            "alias": "OUT: Total",
            "query": "data.site: *",
            "timeField": "metadata.timestamp",
            "datasource": {
                "type": "elasticsearch",
                "uid": "s0TUbLzIz"
            },
            "datasourceId": 10526,
            "intervalMs": 60000,
            "metrics": [
                {
                    "id": "1",
                    "type": "sum",
                    "field": "data.OutBytesPerSec",
                    "settings": {
                        "script": "(_value * 8 / 1024 / 1024)  / (60000 / 1000 / 60)"
                    }
                }
            ],
            "bucketAggs": [
                {
                    "id": "2",
                    "type": "date_histogram",
                    "field": "metadata.timestamp",
                    "settings": {
                        "interval": "auto"
                    }
                }
            ]
        }