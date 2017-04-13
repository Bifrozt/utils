##
### Author: Ruairi Carroll < ruairi.carroll@gmail.com > 
### Purpose: Given a list of hostnames from CLIs, crawl IP-MIB and IF-MIB to get an idea of what is configured where.  
### TODO: Much.

from easysnmp import snmp_get, snmp_set, snmp_walk, Session
from netaddr import * 
import pytricia
import code
import argparse


def main():
    opts = parseArgs()
    pyt = pytricia.PyTricia()
    pyt.insert('0.0.0.0/0', "root")
    pyt.insert('10.0.0.0/8', "RFC1918 root")
    pyt.insert('172.12.0.0/12', "RFC1918 root")
    pyt.insert('192.168.0.0/16', "RFC1918 root")

    prefx = {}
    IGNORED_INTERFACE = [ 'bme0' , 'bme0.32768', 'lo' ]

    for device in opts['hosts']: 
        try:
            session = Session(hostname=device, community=opts['community'], version=2)
            ipent = session.walk('IP-MIB::ipAdEntAddr')
            for item in ipent:
                ip = item.value
                ifIndex = session.get('IP-MIB::ipAdEntIfIndex.' + ip)
                mask = session.get('IP-MIB::ipAdEntNetMask.' + ip)
                ifName = session.get('IF-MIB::ifName.' + ifIndex.value)
                if ifName in IGNORED_INTERFACE:
                    print("Skipping %s" % ifName)
                    continue
                prefix = ip + "/" + str(IPNetwork('0.0.0.0/' + mask.value ).prefixlen)
                pref = IPNetwork(prefix)
                pyt.insert(str(prefix), device + "_" + ifName.value)
        except Exception, err:
            print("\tTIMEOUT: " +fw)
            print("\t" + str(err))
            continue
    ## Print hierarchical tree and exit 
    printTree(pyt)

def prefixDepth(pytree, subnet):
    """Given a subnet in a tree, determine how many levels deep the prefix is. 
    
    Args:
        pytree: A Pytricia tree
        subnet: A string in CIDR notation
    Returns:
        i: int of given depth 
    
    """
    i = 0 
    root = '0.0.0.0/0'
    parent = subnet
    while parent != root:
        i += 1
        parent = pyt.parent(parent)
    return i

def printTree(pytree):
    """Take a given Pytricia tree, print the entire tree in a hierarchial manner 
    
    Args:
        pytree: A PyTricia tree of prefixes.
    Returns:
        Nothing
    
    """
    for subnet in pyt:
        depth = prefixDepth(pyt,subnet)
        print("\t" * depth + " %s" % subnet + " %s" % pyt.get(subnet) )
    return False


def parseArgs():
    """Setup script args, parse then and return them as a dict
    
    Args:
        None
    Returns:
        dict: A dict of all options set on the CLI
    
    """

    help_text = "Crawl your network. -h for help"
    parser = argparse.ArgumentParser(help_text)
    ## Generic args
    parser.add_argument('--community',     help="SNMP community to use")
    parser.add_argument('--hosts',         help="Comma seperated list of hosts")

    args = parser.parse_args()
    host_list = args.hosts.split(',')

    opts = {}
    opts.update({'community': args.community })
    opts.update({'hosts': host_list })

    return opts

if __name__ == "__main__":
     main()
