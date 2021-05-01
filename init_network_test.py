import socket

import dataStructures.node as node
from os import path

if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    server_port_number = 5555
    client_port_number = 5556

    relative_path = "./test_folder"

    test_node = node.Node(relative_path, ip, server_port_number, client_port_number)
    test_node.init_network()
    test_node.load_meta_data()
    test_node.fetch_file("98f4df11-e582-4588-8545-c8c2d125b822")
