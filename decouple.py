import argparse
import socket
import dataStructures.nodev2 as node


def join_network(node: node.Node):

    # new_ip = input("Enter Ip: ")
    server_port = int(input("Server Port: "))
    new_ip = "192.168.1.86"

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
    
    ip = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.") and not ip.endswith('.1')][:1][0]
    server_port_number = args.server_port
    client_port_number = args.client_port
    relative_path = args.shared_folder

    node = node.Node(relative_path, ip, server_port_number, client_port_number)
    print(node.server_port)
    print(node.ip)
    node.repo.load_ignore_file_names()
    node.start_server()
    node.start_worker()

    if args.load:
        node.repo.load_meta_data()
    else:
        node.repo.init_meta_file()

    if not args.init_network:
        join_network(node)
