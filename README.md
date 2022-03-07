# perfSONAR collector to run at UC

[![Build PerfSONAR rucio Logstash dockerhub image](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/ps-collector.yaml/badge.svg)](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/ps-collector.yaml)

To get logstash statistics do:
curl -XGET 'localhost:9600/_node/stats/pipelines/ps-collector?pretty'

and

curl -XGET 'localhost:9600/_node/stats/os?pretty'
curl -XGET 'localhost:9600/_node/hot_threads?pretty'

To check memcached status:

yum install telnet
telnet memcached 11211
stats items

Before starting logstash, make sure that the ps-mapper job at least once finished fine.
One can manually execute it: kubectl create job --from=cronjob/<name of cronjob> <name of job>

To manually flush the cache:
echo 'flush_all' | nc memcached.collectors.svc.cluster.local 11211
