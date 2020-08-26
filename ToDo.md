# g-stream parsing

g12345678901234567890123{"siteID":"mwt2","hostID":"xcache.mwt2.org:9230"}
{"event":"access","accnr":1}
{"bababa"}
{"event":"access","accnr":2}

%{HDR:hdr}%{DATA:id}\n%{JSN:jsn}

HDR g(.|\n|\r){23}
JSN (.|\n|\r)*