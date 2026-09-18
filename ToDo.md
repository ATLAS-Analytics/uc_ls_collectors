# To Do

Done on the `fireflies` branch:

* [x] replace all the "frontier" mentions with "fireflies"
* [x] clean old python related stuff
* [x] change logstash config so its input comes from kafka. Connection details come from environment variables.
* [x] data is stored in ES index fireflies_write

Still open:

* [ ] create the `fireflies-kafka-ca` configmap (ESnet Strimzi cluster CA, key `kafka-ca.pem`) - get the cert from ESnet rather than scraping it off the connection
* [ ] create the `fireflies-kafka` secret (key `password`) in the collectors namespace
* [ ] add the `gitops-uc-ls-fireflies-app-trigger` dispatch target in maniaclab/flux_apps
* [ ] create the `fireflies_write` alias / ILM policy in Elasticsearch
* [ ] decide what, if any, filtering the stardust_firefly payload needs once real documents land
