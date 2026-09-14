# Netstat collector to run at UC

[![Build Netstat Logstash dockerhub image](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/netstat.yaml/badge.svg)](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/netstat.yaml)

Once per hour gets netstat data from all the WLCG sites and puts it into UChicago Elasticsearch.
It gets the data from CERN Monit.

curl -s -X POST 'https://monit-grafana-open.cern.ch/api/ds/query?ds_type=elasticsearch&requestId=SQR103' -H 'Content-Type: application/json' -H 'Accept: application/json'  -d "@request_data.json"

