# perfSONAR collector to run at UC

[![Build PerfSONAR rucio Logstash dockerhub image](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/ps-collector.yaml/badge.svg)](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/ps-collector.yaml)

To get logstash statistics do:
curl -XGET 'localhost:9600/_node/stats/pipelines/ps-collector?pretty'

and

curl -XGET 'localhost:9600/_node/stats/os?pretty'
curl -XGET 'localhost:9600/_node/hot_threads?pretty'
