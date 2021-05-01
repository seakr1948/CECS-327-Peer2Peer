import argparse
import socket
import dataStructures.node as node

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

    if args.init_network:
        node.init_network()

    if args.load:
        node.load_meta_data()
    else:
        node.init_meta_file()
