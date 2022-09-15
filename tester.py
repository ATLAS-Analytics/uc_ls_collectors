import requests

newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}

data = {
    'token': 'sqKHBKJB45n',
    'site': 'MWT2',
    'squid_id': 'asdf',
    'timestamp': 1662047737,
    'hits': 100,
    'requests': 10,
    'cputime': 3,
    'objects': 123,
    'memory': 12314425
}

response = requests.post('https://squid.atlas-ml.org', json=data,
                         headers=newHeaders, verify=False)
print("Status code: ", response.status_code)
