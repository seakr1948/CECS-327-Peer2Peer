import socket

import dataStructures.node as node
from os import path

if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    port_number = 5555

    relative_path = "./test_folder"

    test_node = node.Node(relative_path, ip, port_number)
    test_node.init_network()
    test_node.init_meta_file()
