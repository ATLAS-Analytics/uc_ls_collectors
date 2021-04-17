# To Do

## g-Stream

* make sure it has everything we need
* change all xcaches to send to collector.atlas-ml.org:9000 (LB: 192.170.227.237)

xrootd.monitor dest pfc collector.atlas-ml.org:9000

xrootd.mongstream pfc flush 60s maxlen 1300 send json insthdr collector.atlas-ml.org:9000

parsing

```json
g12345678901234567890123{"siteID":"mwt2","hostID":"xcache.mwt2.org:9230"}
{"event":"access","accnr":1}
{"bababa"}
{"event":"access","accnr":2}

%{HDR:hdr}%{DATA:id}\n%{JSN:jsn}

HDR g(.|\n|\r){23}
JSN (.|\n|\r)*
```

```json
       "message" => "
       {
           "code":"g",
           "pseq": 25,
           "stod":1618516840,
           "sid":176071238409740,
           "src":{
               "site":"",
               "host":"sl-um-es2.slateci.io",
               "port":1094,
               "inst":"atlas-xcache"
            },
            "gs":{
                "type":"C",
                "tbeg":1618638245,
                "tend":1618638253
            }
        }
            
        {
            "event":"file_close",
            "lfn":"atlas/rucio/mc16_13TeV/61/1d/EVNT.18541195._000368.pool.root.1",
            "size":368827877,
            "blk_size":1048576,
            "n_blks":352,
            "n_blks_done":352,
            "access_cnt":2,
            "attach_t":1618638031,
            "detach_t":1618638245,
            "remotes":["st-048-cc8205a3.cern.ch:1095"],
            "b_hit":362827532,
            "b_miss":5699773,
            "b_bypass":0
        }
        
        {
            "event":"file_close",
            "lfn":"atlas/rucio/data18_13TeV/9a/01/DAOD_TOPQ1.23529347._000279.pool.root.1",
            "size":1150928438,
            "blk_size":1048576,
            "n_blks":1098,
            "n_blks_done":1052,
            "access_cnt":4,
            "attach_t":1618637032,
            "detach_t":1618638245,
            "remotes":["ags46.atlas.unimelb.edu.au:1095"],
            "b_hit":85567490,
            "b_miss":291743500,
            "b_bypass":0
        }
        
        {
            "event":"file_close",
            "lfn":"atlas/rucio/mc16_13TeV/c5/ee/DAOD_TOPQ5.22714093._000135.pool.root.1",
            "size":7393431119,
            "blk_size":1048576,
            "n_blks":7051,
            "n_blks_done":7039,
            "access_cnt":4,
            "attach_t":1618628970,
            "detach_t":1618638253,
            "remotes":["sn152.pleiades.uni-wuppertal.de:33145"],
            "b_hit":972730278,
            "b_miss":2930078280,
            "b_bypass":0
        }
            
```


## StashCP

* Move stashcp to stashcp.atlas-ml.org (uses the same LB: 192.170.227.237)

## pilot memory data

```json
{
    "Time": [1606320741, 1606320802, 1606320863, 1606320924, 1606320985, 1606321046, 1606321107],
    "wtime": [17, 79, 138, 199, 263, 322, 384], 
    "stime": [3, 10, 15, 17, 17, 18, 22], 
    "utime": [1, 8, 27, 40, 47, 53, 78], 
    "nprocs": [7, 10, 10, 10, 10, 10, 1], 
    "nthreads": [7, 10, 10, 11, 11, 11, 1], 
    "rchar": [9661182, 29253951, 50758975, 60063417, 66309262, 194864978, 194864978], 
    "read_bytes": [673120256, 1797513216, 2305290240, 2556960768, 2625597440, 2774056960, 2774056960], 
    "wchar": [738743, 1904247, 2300610, 2749777, 2979637, 3052907, 3052907], 
    "write_bytes": [237568, 479232, 851968, 1183744, 1351680, 1409024, 1409024], 
    "pss": [2369, 179744, 237807, 491653, 588889, 879109, 0], 
    "rss": [5224, 183664, 241612, 495164, 592684, 882920, 0], 
    "swap": [0, 0, 0, 0, 0, 0, 0], 
    "vmem": [46696, 929752, 1124256, 1774340, 1878456, 2168092, 0], 
    "rx_bytes": [111714227, 7379763941, 14798824899, 22039708308, 29159085994, 36553874239, 43874232433],
    "rx_packets": [73782, 4876661, 9779219, 14564420, 19269555, 24156279, 28993549], 
    "tx_bytes": [191300, 14308822, 30441615, 47357661, 64118549, 86210443, 109419539], 
    "tx_packets": [2905, 209172, 443100, 686284, 925965, 1247989, 1593046], 
    "type": "MemoryMonitorData", 
    "pandaid": "4903329210"
}
```

## Other

Move both pilot and xcache to SSL
