# TO DO

* get "_id" value too.
* rename columns like this:
    "_id" -> "_id"
    "metadata.timestamp" -> timestamp,
    "data.netsite" -> netsite,
    "data.site" -> site,
    "data.InBytesPerSec" -> InBytesPerSecond,
    "data.OutBytesPerSec" -> OutBytesPerSecond
* add a code to index the data here:
    hosts => "atlas-kibana.mwt2.org"
    ssl_enabled => true
    index       => "wlcg-sitenetwork-%{+YYYY.MM}"
    user => "uc_logstash_indexer"
    password => "${LOGSTASH_PWD}"

