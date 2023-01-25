""" maps ips to sites """

import sys
import json
import requests
import xml.etree.ElementTree as ET
# import socket
from pymemcache.client import base

# suppress InsecureRequestWarning: Unverified HTTPS request is being made.
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


meshes = []
PerfSonars = {}
# throughputHosts = []
# latencyHosts = []

GOCDB_FEED = "https://goc.egi.eu/gocdbpi/public/?method=get_service_endpoint"
OIM_FEED = "https://my.opensciencegrid.org/rgsummary/xml?summary_attrs_showservice=on&summary_attrs_showfqdn=on&gip_status_attrs_showtestresults=on&downtime_attrs_showpast=&account_type=cumulative_hours&ce_account_type=gip_vo&se_account_type=vo_transfer_volume&bdiitree_type=total_jobs&bdii_object=service&bdii_server=is-osg&start_type=7daysago&start_date=11%2F17%2F2014&end_type=now&all_resources=on&facility_sel%5B%5D=10009&gridtype=on&gridtype_1=on&active=on&active_value=1&disable_value=0"


client = base.Client(('memcached', 11211))


class ps:
    hostname = ''
    sitename = ''
    VO = ''
    # ip = ''
    flavor = ''

    def prnt(self):
        print('host:', self.hostname, '\tVO:', self.VO,
              '\tflavor:', self.flavor, '\tsite:', self.sitename)


def request(url, hostcert=None, hostkey=None, verify=False):
    if hostcert and hostkey:
        req = requests.get(url, verify=verify, timeout=120,
                           cert=(hostcert, hostkey))
    else:
        req = requests.get(url, timeout=120, verify=verify)
    req.raise_for_status()
    return req.content


def get_gocdb_sonars(response):
    if not response:
        return None

    tree = ET.fromstring(response)
    gocdb_set = set([(x.findtext('HOSTNAME').strip(),
                      x.findtext('SERVICE_TYPE').strip(),
                      x.findtext('SITENAME').strip(),
                      x.findtext('IN_PRODUCTION')) for x in tree.findall('SERVICE_ENDPOINT')])
    gocdb_sonars = set([(host, stype, site) for host, stype, site, state in gocdb_set if
                        (stype == 'net.perfSONAR.Bandwidth' or stype == 'net.perfSONAR.Latency')])
    return gocdb_sonars


def get_oim_sonars(response):
    if not response:
        return None

    tree = ET.fromstring(response)
    oim_resources = list()
    res_groups = tree.findall('ResourceGroup')
    for res in res_groups:
        site = res.findtext('GroupName')
        try:
            oim_resources.extend([(x.findtext('FQDN').strip(),
                                   x.findtext('Services/Service/Name').strip(),
                                   site) for x in res.findall('Resources/Resource')])
            for r in res.findall('Resources/Resource'):
                oim_resources.extend([(x.findtext('Details/endpoint').strip(),
                                       x.findtext('Name').strip(),
                                       site) for x in r.findall('Services/Service')])
        except AttributeError:
            continue
    oim_sonars = set([(host, stype, site) for host, stype, site in oim_resources if
                      stype == 'net.perfSONAR.Bandwidth' or stype == 'net.perfSONAR.Latency'])
    return oim_sonars


def reload():
    print('starting mapping reload')
    global throughputHosts
    global latencyHosts

    # timeout = 60
    # socket.setdefaulttimeout(timeout)

    print(" --- getting sites from ATLAS CRIC ---")
    try:
        r = requests.get(
            'https://atlas-cric.cern.ch/api/core/site/query/?json&vo_name=atlas&state=ACTIVE', verify=False)
        res = r.json()
        # print('whole json:', res)
        sites = []
        for _key, val in res.items():
            sites.append(val["rc_site"])
        print(len(sites), "sites reloaded.")
    except:
        print("Could not get sites from CRIC. Exiting...")
        print("Unexpected error: ", str(sys.exc_info()[0]))

    print(" --- getting PerfSonars from ATLAS CRIC ---")
    try:
        r = requests.get(
            'https://atlas-cric.cern.ch/api/core/service/query/?json&state=ACTIVE&type=PerfSonar',
            verify=False
        )
        res = r.json()
        for _key, val in res.items():
            # print(_key, val)
            p = ps()
            try:
                p.hostname = val['endpoint']

                # try: NOT LOOKING UP IP addresses as that will be done by enrich.rb
                #     p.ip = socket.gethostbyname(p.hostname)
                # except socket.gaierror as e:
                #     p.ip = '0.0.0.0'
                #     print(p.hostname, e)

                p.production = False
                if 'status' in val:
                    if val['status'] == 'production':
                        p.production = True

                p.flavor = val.get('flavour', 'unknown')
                p.sitename = val.get('rcsite', "unknown")

                if p.sitename in sites:
                    p.VO = "ATLAS"
                else:
                    p.VO = "unknown"

                if p.sitename not in sites:
                    sites.append(p.sitename)

                client.set('vo_'+p.hostname, p.VO)
                client.set('si_'+p.hostname, p.sitename)
                client.set('pr_'+p.hostname, p.production)
                PerfSonars[p.hostname] = p
            except AttributeError as e:
                print('attribute missing.', e)
            p.prnt()

        print(len(PerfSonars.keys()), 'perfsonars reloaded.')
    except:
        print("Could not get perfsonars from CRIC. Exiting...")
        print("Unexpected error: ", str(sys.exc_info()[0]))

    # gocdb/oim processing =============================

    try:
        print("Retrieving GOCDB sonars ...")
        sonars = list(get_gocdb_sonars(request(GOCDB_FEED, verify=False)))
        print("Retrieving OIM sonars ...")
        oim_sonars = list(get_oim_sonars(request(OIM_FEED)))
        sonars.extend(oim_sonars)

        for host, stype, site in sonars:
            if host in PerfSonars.keys():
                continue
            p = ps()
            p.hostname = host
            p.production = False
            p.VO = "unknown"
            p.flavor = stype
            p.sitename = site

            client.set('vo_'+p.hostname, p.VO)
            client.set('si_'+p.hostname, p.sitename)
            client.set('pr_'+p.hostname, p.production)

            PerfSonars[p.hostname] = p
            p.prnt()
        print('Done')
    except:
        print("Could not get perfSONARs from GOCDB/OIM ...")
        print("Unexpected error: ", str(sys.exc_info()[0]))

    print('All done.')


if __name__ == "__main__":
    reload()
