import nmap
import socket
import os.path as path

def find_ips_on_network():
    ps = nmap.PortScanner()
    network = '192.168.1.0/24'
    ps.scan(hosts=network, arguments='-sn')
    ips_on_network = [(host, ps[host]['status']['state']) for host in ps.all_hosts()]
    
    return ips_on_network

def find_open_ports(ip: str):
    ps = nmap.PortScanner()
    ps.scan(ip, '3990-4001')
    print(ps[ip])

if __name__ == "__main__":
    ips = find_ips_on_network()
    find_open_ports(ips[len(ips) - 1][0])