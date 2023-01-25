import logging
import requests
import xml.etree.ElementTree as ET
import socket
import psconfig.api

# from ncgx.inventory import Hosts, Checks, Groups

# suppress InsecureRequestWarning: Unverified HTTPS request is being made.
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

log = logging.getLogger('ncgx')

PS_LCORE_METRICS = (
    'perfSONAR services: owamp',
    'perfSONAR services: twamp',
)

PS_CORE_METRICS = (
    'perfSONAR services: pscheduler/ipv4',
)

PS_TOOLKIT_METRICS = (
    'perfSONAR json summary',
    'perfSONAR services: ntp',
    'perfSONAR services: versions',
    'perfSONAR services: pscheduler stats',
    'perfSONAR configuration: meshes',
    'perfSONAR configuration: contacts',
    'perfSONAR configuration: location',
    'perfSONAR services: pscheduler daemon',
    'perfSONAR hardware check'
)


def request(url, hostcert=None, hostkey=None, verify=False):
    if hostcert and hostkey:
        req = requests.get(url, verify=verify, timeout=120, cert=(hostcert, hostkey))
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
                      x.findtext('IN_PRODUCTION'))
                     for x in tree.findall('SERVICE_ENDPOINT')])
    gocdb_sonars = set([(host, stype) for host, stype, state in gocdb_set
                        if (stype == 'net.perfSONAR.Bandwidth' or stype == 'net.perfSONAR.Latency')])
    return gocdb_sonars


def get_oim_sonars(response):
    if not response:
        return None
    tree = ET.fromstring(response)
    oim_resources = list()
    # first take all services defined via details/endpoint
    for r in tree.findall('ResourceGroup/Resources/Resource'):
        try:
            oim_resources.extend([(x.findtext('Details/endpoint').strip(),
                                   x.findtext('Name').strip())
                                  for x in r.findall('Services/Service')])
        except AttributeError:
            continue

    # then complement this with services with just FQDN
    res_index = set([entry[0] for entry in oim_resources])
    for x in tree.findall('ResourceGroup/Resources/Resource'):
        h = x.findtext('FQDN').strip()
        st = x.findtext('Services/Service/Name').strip()
        if h not in res_index:
            oim_resources.append((h, st))

    oim_sonars = set([(host, stype) for host, stype in oim_resources
                      if stype == 'net.perfSONAR.Bandwidth' or stype == 'net.perfSONAR.Latency'])
    return oim_sonars


def get_fqdn(host):
    try:
        socket.getaddrinfo(host, 80, 0, 0, socket.IPPROTO_TCP)
    except socket.gaierror:
        return False
    return True


def run(mesh, gocdb, oim, hostcert, hostkey, wato_hosts):
    log.info("Retrieving meshes ...")
    mesh_config = psconfig.api.PSConfig(mesh)
    mc_hosts = mesh_config.get_all_hosts()

    log.info("Retrieving GOCDB sonars ...")
    sonars = list(get_gocdb_sonars(request(gocdb+"&service_type=net.perfSONAR.Latency")))
    sonars_b = list(get_gocdb_sonars(request(gocdb+"&service_type=net.perfSONAR.Bandwidth")))
    sonars.extend(sonars_b)

    log.info("Retrieving OIM sonars ...")
    oim_sonars = list(get_oim_sonars(request(oim)))
    sonars.extend(oim_sonars)

    sonars_set = set()
    for h, _ in sonars:
        sonars_set.add(h)

    non_registered = mc_hosts - sonars_set
    not_in_mesh = sonars_set - mc_hosts
    log.warning("Hosts listed in meshes, but not registered in GOCDB/OIM: {}".format(non_registered))
    log.warning("Hosts registered, but not in any mesh: {}".format(not_in_mesh))
    print("Done.")
    # hosts = Hosts()
    # for host in mc_hosts:
    #     if get_fqdn(host):
    #         hosts.add(host, mesh_config.get_test_types(host))
    # for host, stype in sonars:
    #     if host not in mc_hosts and get_fqdn(host):
    #         hosts.add(host, (stype, ))

    # hosts.serialize()

    # hg = Groups("host_groups")
    # for mesh, mesh_members in mesh_config.get_config_host_map().items():
    #     mesh = mesh.replace('Mesh Config', '').strip()
    #     for host in mesh_members:
    #         hg.add(mesh, host)
    # hg.serialize()

    # c = Checks()
    # # core metrics
    # c.add_all(PS_CORE_METRICS, tags=["latency", "latencybg", "throughput", "trace",
    #                                  "net.perfSONAR.Latency", "net.perfSONAR.Bandwidth"])
    # c.add_all(PS_LCORE_METRICS, tags=["latency", "latencybg", "net.perfSONAR.Latency"])
    # all_hosts = hosts.get_all_hosts()
    # for host in all_hosts:   # ipv6-only core metrics
    #     host_addr = socket.getaddrinfo(host, 80, 0, 0, socket.IPPROTO_TCP)
    #     ip6 = filter(lambda x: x[0] == socket.AF_INET6, host_addr)
    #     if ip6:
    #         c.add('perfSONAR services: pscheduler/ipv6', hosts=(host,))

    # # freshness metrics
    # c.add('perfSONAR esmond freshness: latency', tags=["latencybg", "latency"])
    # c.add('perfSONAR esmond freshness: throughput', tags=["throughput", ])
    # c.add('perfSONAR esmond freshness: trace', tags=["trace", ])
    # # toolkit metrics
    # for host in all_hosts:
    #     if 'es.net' in host or 'geant' in host or 'internet2' in host:
    #         continue
    #     else:
    #         c.add_all(PS_TOOLKIT_METRICS, hosts=(host, ))

    # c.serialize()
