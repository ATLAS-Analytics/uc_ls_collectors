# EventLoop Logstash collector to run at UC

[![Build EventLoop Monitor Logstash dockerhub image](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/EventLoop.yaml/badge.svg)](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/EventLoop.yaml)

This receives data from rucio-indexer running in river-dev/collectors. Rucio-indexer sends rucio-events and rucio-traces directly to Elasticsearch, while rucio-nongrid-traces go to this logstash and then to Elasticsearch.
