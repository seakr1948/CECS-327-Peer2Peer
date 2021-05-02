import argparse
import socket
import dataStructures.node as node


def join_network(node: node.Node):

    # new_ip = input("Enter Ip: ")
    # server_port = int(input("Server Port: "))
    new_ip = "192.168.1.86"
    server_port = 5512

    node.request_network_join(new_ip, server_port, network_key=9999)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "shared_folder", help="relative path of shared folder", type=str
    )
    parser.add_argument("server_port", help="port that listens for request", type=int)
    parser.add_argument("client_port", help="port that broadcast changes", type=int)
    parser.add_argument("--init_network", help="starts network", action="store_true")
    parser.add_argument(
        "--load", help="loads meta file, otherwise init meta file", action="store_true"
    )

    args = parser.parse_args()

    ip = socket.gethostbyname(socket.gethostname())
    server_port_number = args.server_port
    client_port_number = args.client_port
    relative_path = args.shared_folder

    node = node.Node(relative_path, ip, server_port_number, client_port_number)
    node.node_data_handler.load_ignore_file_names()
    node.server.start_server()
    node.start_worker

    if args.load:
        node.node_data_handler.load_meta_data()
    else:
        node.node_data_handler.init_meta_file()

    if args.init_network:
        node.node_data_handler.init_network()
    else:
        join_network(node)
