# Logstash collectors to run at UC

[![Build Memory Monitor image](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/MemoryMonitor.yaml/badge.svg)](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/MemoryMonitor.yaml)

    * Pilot sends memory data to pilot.atlas-ml.org - this is done through ingress controller.
    * Pilot does not send Benchmark data at the moment
    * ATLASrift - visits - not running now.
    * xCache:
        * from reporter and nodes - xcache.atlas-ml.org:80 - ingress controller xcache.yaml
        * gStream - port 9000 UDP - collector.atlas-ml.org - load balancer
        * StashCP - port 9951 TCP collector.atlas-ml.org - load balancer
    * RUCIO-events collector - not sending now. sent directly to ES
    * x1t jobs info - not configured?
