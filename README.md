# Frontier collector to run at UC

[![Build Frontier Logstash dockerhub image](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/frontier.yaml/badge.svg)](https://github.com/ATLAS-Analytics/uc_ls_collectors/actions/workflows/frontier.yaml)

If it gets frontier-id field, It splits it into task_id and job_id.
Enriching with panda.reqid and panda.taskname is done manually in this way:

* in kibana there is an Enrich Policy in "Index Management" named *panda_to_frontier*. It matches tasks table *jeditaskid* and get fields: *reqid*, *taskname*.
* we reindex frontier data where the fields are not present.

These are console commands:

POST /_enrich/policy/panda_to_frontier/_execute?wait_for_completion=true

if index got rolled over, unlock it:
PUT neo_frontier-000008/_settings
{ "index.blocks.write": false }

POST /neo_frontier-000008/_update_by_query?pipeline=frontier_enrichment&conflicts=proceed&slices=auto&requests_per_second=5000&wait_for_completion=false
{
  "query": {
    "bool": {
      "must": [
        {"exists":{"field":"task_id"}}
      ],
      "must_not": [ { "exists": { "field": "panda.reqid" } } ]
    }
  }
}