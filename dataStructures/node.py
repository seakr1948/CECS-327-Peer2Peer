from io import BytesIO
import json
import socket
import uuid
import dataStructures.file as file_
import communication.data_transmitters as data_transmitters
from fileSystemHelpers.Watcher import Watcher
import logging
import threading
import traceback

from os import path, sendfile, waitpid
from os import walk
from queue import LifoQueue


class Node:
    def __init__(
        self,
        shared_folder_relative_path: str,
        ip: str,
        server_port: str,
        client_port: str,
        network_key=9999,
        uuid: uuid.UUID = uuid.uuid4(),
    ):

        # Standard node data
        self.folder_relative_path = shared_folder_relative_path
        self.folder_complete_path = path.abspath(self.folder_relative_path)
        self.ip = ip
        self.server_port = server_port
        self.client_port = client_port
        self.encoder = [9, 4, 3, 6]
        self.network_key = network_key
        self.ignore_file_names = []

        self.uuid = uuid
        self.peers = {}
        print(uuid)

        # Meta data path
        self.meta_data_path = path.join(self.folder_complete_path, "meta.json")
        self.node_data_handler = DataHandler(self)

        # Work buffer for the client
        self.work_buffer = LifoQueue()
        self.client = Client(self)
        self.server = Server(self)

        self.WORK = {
            "SEND_REQUEST": self.client.send_request,
            "SERVE_FILE": self.client.send_file,
            "FETCH_FILE": self.request_file,
        }

    def start_worker(self):
        start_a_thread(self.wait_for_work)

    def start_watcher(self):
        start_a_thread(self.wait_for_file_update)

    def wait_for_work(self):
        # While true block for work
        while True:
            try:
                work = self.work_buffer.get(block=True)
                print(work["TYPE"])
                self.WORK[work["TYPE"]](work["DATA"])
            except:
                traceback.print_exc()

    def wait_for_file_update(self):
        # While true block for file updates
        while True:
            update = self.file_watcher.event_queue.get(block=True)
            print(update)

    def add_uuid_to_worker(self, file_uuids, node_uuid):
        for uuid in file_uuids:
            self.add_work_to_worker(
                {"TYPE": "FETCH_FILE", "DATA": {"FILE": uuid, "NODE": node_uuid}}
            )

    def add_work_to_worker(self, work):
        self.work_buffer.put(work)

    def build_join_request(self, network_key):
        self.node_data_handler.load_meta_data()
        return {
            "TYPE": "JOIN",
            "DATA": {
                "NETWORK_KEY": network_key,
                "FILES": [file_uuid for file_uuid in self.meta_data.keys()],
                "NODE_DATA": self.node_data_handler.get_node_meta_data(),
            },
        }

    def request_network_join(self, ip, port, network_key):
        data = {
            "IP": ip,
            "SERVER_PORT": port,
            "REQUEST": self.build_join_request(network_key),
        }
        self.client.send_request(data)

    def handle_join_request(self, data):
        if (
            data["NETWORK_KEY"] == self.network_key
            and data["NODE_DATA"]["UUID"] not in self.peers
        ):
            work = {
                "TYPE": "SEND_REQUEST",
                "DATA": {
                    "REQUEST": self.build_join_request(self.network_key),
                    "IP": data["NODE_DATA"]["IP"],
                    "SERVER_PORT": data["NODE_DATA"]["SERVER_PORT"],
                },
            }
            self.add_work_to_worker(work)
            self.handle_network_accept(data)

    def handle_network_accept(self, data):
        self.node_data_handler.add_peer(data["NODE_DATA"])
        self.add_uuid_to_worker(data["FILES"], data["NODE_DATA"]["UUID"])

    def request_file(self, data):
        node_id = data["NODE"]
        data = {
            "IP": self.peers[node_id]["IP"],
            "SERVER_PORT": self.peers[node_id]["SERVER_PORT"],
            "REQUEST": {
                "TYPE": "FETCH_FILE",
                "DATA": {"FILE": data["FILE"], "NODE": str(self.uuid)},
            },
        }

        self.client.send_request(data)

    def handle_file_request(self, data):
        file_id = data["FILE"]
        node_id = data["NODE"]

        file_meta_data = self.node_data_handler.fetch_file_data(file_id)
        file_buffer = self.node_data_handler.fetch_file(file_id)

        work = {
            "TYPE": "SERVE_FILE",
            "DATA": {
                "META_DATA": {"FILE": file_id, "META_DATA": file_meta_data},
                "FILE_CONTENT": file_buffer,
                "NODE": node_id,
            },
        }

        self.add_work_to_worker(work)

    def handle_file_add(self, data):
        file_id = data["META_DATA"]["FILE"]
        file_data = data["META_DATA"]["META_DATA"]
        file_content_bytes = data["FILE_CONTENT"]

        self.node_data_handler.add_file(file_id, file_data, file_content_bytes)


class DataHandler:
    def __init__(self, node: Node):
        self.node = node

    def __str__(self):
        return str(self.node.uuid) + "\n" + str(self.node.peers)

    def init_network(self):

        # Starts a dict of peers
        self.node.peers = {}

    def add_ignore_files(self, file_names: list):
        file_names = [name.strip('\n') for name in file_names]
        print(file_names)
        self.node.ignore_file_names.extend(file_names)

    def load_ignore_file_names(self):
        print("here")
        try:
            print("GETING PATH")
            path_ = path.join(self.node.folder_complete_path, '.ignore')
            print(path_)
            with open(
               path_
            ) as file_names:
                self.add_ignore_files(file_names.readlines())
        except:
            print("No ignored files")

        print(self.node.ignore_file_names)

    def init_meta_file(self):
        file_structure = []

        # Walk the tree of the directory and append a zipped stucture of directory and file names
        for (dirpath, dirnames, filenames) in walk(self.node.folder_complete_path):
            file_structure.append((dirpath, filenames))

        file_objects = []
        # Loop through each directory
        for folder in file_structure:
            folder_files = folder[1]  # Files in directory
            complete_folder_path = folder[0]  # Path of the directory

            # Loop through each file name in directory
            for file in folder_files:
                # If not part of the ignore files
                if file not in self.node.ignore_file_names:
                    # Compute the relative path of the file
                    paths = [
                        path.relpath(
                            complete_folder_path, self.node.folder_relative_path
                        ),
                        file,
                    ]
                    relative_path_of_file = path.join(*paths)

                    # Make a File object out of it, see: dataStuctures.file
                    file_objects.append(
                        file_.File(
                            self.node.folder_complete_path,
                            relative_path_of_file,
                            self.node.uuid,
                            self.node.encoder,
                        )
                    )

        # Get all meta_data from each file in a list
        meta_data = {}
        for file in file_objects:
            meta_data.update(file.to_dict())

        self.write_to_meta_data_file(meta_data)

    def write_to_meta_data_file(self, data):
        # Open meta data
        meta_data_file = open(self.node.meta_data_path, "w")

        # Make a jsonstring out of the data and write to the file
        json.dump(
            data,
            meta_data_file,
            indent=4,
            separators=(", ", ": "),
            sort_keys=True,
        )

        # Close file
        meta_data_file.close()

    def load_meta_data(self):

        try:
            path_to_meta = path.join(self.node.folder_complete_path, "meta.json")
            file = open(path_to_meta, "r")

            self.node.meta_data = json.loads(file.read())
        except:
            print("meta does not exist")

    def update_file_meta_data(self, file_uuid, meta_data):
        self.load_meta_data()
        self.node.meta_data.update({file_uuid: meta_data})
        self.write_to_meta_data_file(self.node.meta_data)

    def get_node_meta_data(self):
        return {
            "UUID": str(self.node.uuid),
            "IP": self.node.ip,
            "SERVER_PORT": self.node.server_port,
        }

    def add_peer(self, peer_data):
        if hasattr(self.node, "peers"):
            self.node.peers = {}

        self.node.peers.update(
            {
                peer_data["UUID"]: {
                    "IP": peer_data["IP"],
                    "SERVER_PORT": peer_data["SERVER_PORT"],
                }
            }
        )

        print("PEERS: " + str(self.node.peers.keys()))

    def fetch_file_data(self, uuid_str):
        self.load_meta_data()
        return self.node.meta_data[uuid_str]

    def fetch_file(self, uuid_str):
        file_meta_data = self.fetch_file_data(uuid_str)

        relative_file_path = file_meta_data["relative_path"]
        complete_file_path = path.join(
            self.node.folder_complete_path, relative_file_path
        )

        file_bytes = open(complete_file_path, "rb")

        copy_of_file = BytesIO(file_bytes.read())

        file_bytes.close()

        return copy_of_file

    def add_file(self, file_uuid, meta_data, file_content):
        self.update_file_meta_data(file_uuid, meta_data)
        self.write_file_content(meta_data["relative_path"], file_content)

    def write_file_content(self, relative_path, file_content: BytesIO):
        file = open(path.join(self.node.folder_complete_path, relative_path), "wb")
        file.write(file_content.read())
        file.close()

    def update_file_meta(self, file_uuid, updated_meta: dict):
        self.load_meta_data()
        file_meta_data = self.node.meta_data[file_uuid]

        for key in updated_meta.keys():
            file_meta_data.update({key: updated_meta[key]})


class Client:
    def __init__(self, node: Node):
        self.node = node
        self.set_up_client_socket()
        self.file_watcher = Watcher(self.node.folder_complete_path)

    def set_up_client_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_request(self, data):
        ip = data["IP"]
        port = data["SERVER_PORT"]
        request = data["REQUEST"]
        try:
            # Send join request
            data_transmitters.send_json(self.client_socket, request)

        except:
            self.client_socket.connect((ip, port))

        # Send join request
        data_transmitters.send_json(self.client_socket, request)
        print(self.client_socket)
        print("sent")

        return self.client_socket

    def send_file(self, data):
        ip = self.node.peers[data["NODE"]]["IP"]
        port = self.node.peers[data["NODE"]]["SERVER_PORT"]

        file_buffer = data["FILE_CONTENT"]
        file_meta_data = data["META_DATA"]

        header = {"TYPE": "RECV_FILE", "DATA": "INCOMING_FILE"}

        try:
            # Send join request
            data_transmitters.send_file(
                self.client_socket, file_buffer, file_meta_data, header
            )

        except:
            self.client_socket.connect((ip, port))

        # Send join request
        data_transmitters.send_file(
            self.client_socket, file_buffer, file_meta_data, header
        )

        return self.client_socket


class Server:
    def __init__(self, node: Node):
        self.node = node

        # List of possible request and the function to handle it
        self.REQUEST = {
            "JOIN": self.node.handle_join_request,
            "FETCH_FILE": self.node.handle_file_request,
            "RECV_FILE": self.node.handle_file_add,
        }

    def start_server(self):
        # Start listening for request
        self.set_up_request_socket()

    def set_up_request_socket(self):
        # Create a new socket and bind it to the node IP
        self.request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.request_socket.bind((self.node.ip, self.node.server_port))
        # Start request dispatching
        start_a_thread(self.dispatch_request)

    def dispatch_request(self):
        # Listen for request
        self.request_socket.listen(5)
        while True:
            # Accept connection
            connection, address = self.request_socket.accept()
            print("Accepted")
            # Dispatch a new thread to carry out request
            start_a_thread(self.handle_request, (connection,))
            print(connection)

    def handle_request(self, connection):
        while True:
            # Grab the request
            request = data_transmitters.receive_json(connection)
            self.echo_request(request)

            try: 
                # Get the type of request
                type_of_request = request["TYPE"]
                print("REQUEST TYPE: " + type_of_request)
                if type_of_request == "RECV_FILE":
                    self.recv_file(connection)
                    continue
            except:
                continue

            # Use the type to call the right function
            # Pass the data in the request to that function
            try:
                self.REQUEST[type_of_request](request["DATA"])
            except:
                traceback.print_exc()
                print("REQUEST not set up yet")
        
        connection.close()

    def recv_file(self, connection):
        meta_data, file_buffer = data_transmitters.receive_file(connection)
        data = {"META_DATA": meta_data, "FILE_CONTENT": file_buffer}
        self.REQUEST["RECV_FILE"](data)

    def serve_file(self, connection):
        pass

    def echo_request(self, request):
        print(request)


def start_a_thread(function, args_=()):
    thread = threading.Thread(target=function, args=args_)
    thread.start()
