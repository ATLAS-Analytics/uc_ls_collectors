""" maps ips to sites """

import sys
import json
import requests
import xml.etree.ElementTree as ET
import psconfig.api
from pymemcache.client import base

# suppress InsecureRequestWarning: Unverified HTTPS request is being made.
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


meshes = []
PerfSonars = {}

client = base.Client(('memcached', 11211))


class ps:
    hostname = ''
    sitename = ''
    flavor = ''
    VO = []

    def prnt(self):
        print('host:', self.hostname,
              '\tflavor:', self.flavor, '\trcsite:', self.rcsite, '\tvo:', self.VO)


def request(url, hostcert=None, hostkey=None, verify=False):
    if hostcert and hostkey:
        req = requests.get(url, verify=verify, timeout=120,
                           cert=(hostcert, hostkey))
    else:
        req = requests.get(url, timeout=120, verify=verify)
    req.raise_for_status()
    return req.content


def reload():
    print('starting mapping reload')

    # timeout = 60
    # socket.setdefaulttimeout(timeout)

    # print(" --- getting sites from WLCG CRIC ---")
    # try:
    #     r = requests.get(
    #         'https://wlcg-cric.cern.ch/api/core/site/query/?json&state=ACTIVE', verify=False)
    #     res = r.json()
    #     # print('whole json:', res)
    #     sites = []
    #     for _key, val in res.items():
    #         sites.append(val["rc_site"])
    #     print(len(sites), "sites reloaded.")
    # except:
    #     print("Could not get sites from CRIC. Exiting...")
    #     print("Unexpected error: ", str(sys.exc_info()[0]))

    print(" --- getting PerfSonars from WLCG CRIC ---")
    try:
        r = requests.get(
            'https://wlcg-cric.cern.ch/api/core/service/query/?json&state=ACTIVE&type=PerfSonar',
            verify=False
        )
        res = r.json()
        for _key, val in res.items():
            # print(_key, val)
            p = ps()
            try:
                p.hostname = val['endpoint']  # host name as in pwa
                p.production = False
                p.flavor = val.get('flavour', 'unknown')
                p.rcsite = val.get('rcsite', "unknown")

                usage = val.get('usage', 'unknown')
                for exp in usage:
                    setattr(p, exp+'_site', usage[exp][0]['site'])
                    p.VO.append(exp)

                PerfSonars[p.hostname] = p
            except AttributeError as e:
                print('attribute missing.', e)
            p.prnt()

        print(len(PerfSonars.keys()), 'perfsonars reloaded.')
    except:
        print("Could not get perfsonars from CRIC. Exiting...")
        print("Unexpected error: ", str(sys.exc_info()[0]))

    print('All done.')


if __name__ == "__main__":
    reload()
