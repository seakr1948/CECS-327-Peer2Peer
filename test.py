import socket

import dataStructures.node as node
from os import path

if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())

    relative_path = "./test_folder"

    test_node = node.node(relative_path, ip, "5555")

    test_node.init_network()
    test_node.init_meta_file()