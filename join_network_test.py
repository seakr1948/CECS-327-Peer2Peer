import socket

import dataStructures.node as node
from os import path

if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    port_number = 5555
    print(ip)
    
    relative_path = "./test_folder"

    test_node = node.Node(relative_path, ip, port_number)

    host_ip  = "192.168.1.86"
    network_key = 9999
    test_node.start_a_thread(test_node.request_join_network, args_= (host_ip, port_number, ip))
