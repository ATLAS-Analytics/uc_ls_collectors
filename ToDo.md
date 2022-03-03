# To Do

* add run.end-time as timestamp
* add @timestamp as archiver_timestamp
* add ingest_timestamp
* create memcache
* if IP not in cache, add it.
* memcache will set a lifetime to lookups.
* mc will have another cron that looks up all the instances in CRIC add them to cache.

* add src/dest after IP lookup from cache. if it was not found find it and cache result.
