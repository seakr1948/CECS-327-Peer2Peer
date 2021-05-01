import argparse
import socket
import dataStructures.node as node

def join_network(node: node.Node):

    new_ip = input("Enter Ip: ")
    server_port = int(input("Server Port: "))

    node.client.request_join_network(new_ip, server_port, network_key=9999)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("shared_folder", help="relative path of shared folder", type=str)
    parser.add_argument("server_port", help="port that listens for request", type=int)
    parser.add_argument("client_port", help="port that broadcast changes", type=int)
    parser.add_argument("--init_network", help="starts network", action="store_true")
    parser.add_argument("--load", help="loads meta file, otherwise init meta file", action="store_true")

    args = parser.parse_args()

    ip = socket.gethostbyname(socket.gethostname())
    server_port_number = args.server_port
    client_port_number = args.client_port
    relative_path = args.shared_folder

    node = node.Node(relative_path, ip, server_port_number, client_port_number)
    node.load_ignore_file_names()

    if args.load:
        node.load_meta_data()
    else:
        node.init_meta_file()

    if args.init_network:
        node.init_network()
    else:
        join_network(node)


