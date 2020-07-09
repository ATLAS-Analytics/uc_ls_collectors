FROM docker.elastic.co/logstash/logstash:7.8.0

LABEL maintainer="Ilija Vukotic <ivukotic@cern.ch>"

USER root
RUN yum install -y nmap

# USER logstash

RUN mkdir /usr/share/logstash/rucio
RUN mkdir /usr/share/logstash/pilot
RUN mkdir /usr/share/logstash/atlasrift
RUN mkdir /usr/share/logstash/xcache
RUN mkdir /usr/share/logstash/stashcp

RUN mkdir /usr/share/logstash/templates

RUN bin/logstash-plugin install logstash-input-stomp

COPY logstash.yml /usr/share/logstash/config/
COPY pipelines.yml /usr/share/logstash/config/

# COPY pipelines/rucio-events.conf  /usr/share/logstash/rucio/
# COPY pipelines/PandaPilot.conf  /usr/share/logstash/pilot/
# COPY pipelines/ATLASrift.conf /usr/share/logstash/atlasrift/
# COPY pipelines/xCacheMonitoringCollector.conf /usr/share/logstash/xcache/
COPY pipelines/xCache_gStreamCollector.conf /usr/share/logstash/xcache/
# COPY pipelines/StashCP.conf  /usr/share/logstash/stashcp/

# COPY templates/ATLASrift.template  /usr/share/logstash/templates/