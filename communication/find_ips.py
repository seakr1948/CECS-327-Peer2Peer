import nmap as nmap
from nmap import PortScanner
import socket
import os.path as path

def find_ips_on_network(network):
    ps = PortScanner()
    ps.scan(hosts=network, arguments="-sn")
    ips_on_network = [(host, ps[host]["status"]["state"]) for host in ps.all_hosts()]

    return ips_on_network

if __name__ == "__main__":
    ips = find_ips_on_network()
    print(ips)
