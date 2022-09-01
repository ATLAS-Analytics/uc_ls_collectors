import requests

newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}

response = requests.post('https://squid.atlas-ml.org', json={'id': 1, 'name': 'Jessa'},
                         headers=newHeaders)

print("Status code: ", response.status_code)
print("Printing Entire Post Request")
print(response.json())
