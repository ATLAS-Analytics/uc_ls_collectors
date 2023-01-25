""" maps ips to sites """

import sys
import requests
import psconfig.api
from pymemcache.client import base

# suppress InsecureRequestWarning: Unverified HTTPS request is being made.
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

PerfSonars = {}

print('loading pwa nodes')
psc = psconfig.api.PSConfig('https://psconfig.aglt2.org/pub/config',
                            hostcert=None, hostkey=None, verify=False)
prod_hosts = psc.get_all_hosts()
print(f'found {len(prod_hosts)} production hosts in PWA')

client = base.Client(('memcached', 11211))


class ps:
    def __init__(self, hostname):
        self.VO = []
        self.sitename = []
        self.hostname = hostname
        self.rcsite = ''
        self.flavor = ''
        self.production = False
        if self.hostname in prod_hosts:
            self.production = True

    def __str__(self):
        s = f'host: {self.hostname} \tprod: {self.production} \tflavor: {self.flavor}'
        s += f'\trcsite: {self.rcsite} \tvo: {self.VO} \tsitename:{self.sitename}'
        return s


def request(url, hostcert=None, hostkey=None, verify=False):
    if hostcert and hostkey:
        req = requests.get(url, verify=verify, timeout=120,
                           cert=(hostcert, hostkey))
    else:
        req = requests.get(url, timeout=120, verify=verify)
    req.raise_for_status()
    return req.content


def reload():
    print(" --- getting PerfSonars from WLCG CRIC ---")
    r = requests.get(
        'https://wlcg-cric.cern.ch/api/core/service/query/?json&state=ACTIVE&type=PerfSonar',
        verify=False
    )
    res = r.json()
    for _key, val in res.items():
        if not val['endpoint']:
            print('no hostname? should not happen:', val)
            continue
        p = ps(val['endpoint'])

        try:
            p.flavor = val.get('flavour', 'unknown')
            p.rcsite = val.get('rcsite', "unknown")
            usage = val.get('usage', {})
            for exp in usage:
                p.VO.append(exp)
                p.sitename.append(usage[exp][0]['site'])

            client.set('vo_'+p.hostname, ','.join(p.VO))
            client.set('sitename_'+p.hostname, ','.join(p.sitename))
            client.set('rcsite_'+p.hostname, p.rcsite)
            client.set('production_'+p.hostname, p.production)

            PerfSonars[p.hostname] = p
        except AttributeError as e:
            print('attribute missing.', e)
        print(p)

    print(len(PerfSonars.keys()), 'perfsonars reloaded.')


if __name__ == "__main__":
    reload()
