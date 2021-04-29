import socket

import dataStructures.node as node
from os import path

if __name__ == "__main__":
    new_network = input("Start a newtork? [Y/n]: ")
    port_number = int(input("Port Number: "))
    ip = socket.gethostbyname(socket.gethostname())

    print("IP: " + ip)

    relative_path = "./test_folder"

    test_node = node.Node(relative_path, ip, port_number)

    if new_network.upper() == 'Y':
        test_node.init_network()
        test_node.start_a_thread(test_node.listen_for_request)
    else:
        network_key = input("Enter network key: ")
        host_ip = input("Enter ip to join: ")
        test_node.start_a_thread(test_node.request_join_network, args_= (host_ip, port_number, ip))

    test_node.init_meta_file()