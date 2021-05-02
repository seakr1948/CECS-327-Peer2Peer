import json
import socket
import uuid
import dataStructures.file as file_
import communication.data_transmitters as data_transmitters
from fileSystemHelpers.Watcher import Watcher
import logging
import threading
import traceback

from os import path
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

        # Meta data path
        self.meta_data_path = path.join(self.folder_complete_path, "meta.json")

        # Work buffer for the client
        self.work_buffer = LifoQueue()
        self.client = Client(self)
        self.server = Server(self)

    def __str__(self):
        return str(self.uuid) + "\n" + str(self.peers)

    def init_network(self):

        # Starts a dict of peers
        self.peers = {}

    def add_ignore_files(self, file_names: list):
        self.ignore_file_names.extend(*file_names)

    def load_ignore_file_names(self):
        try:
            with open(
                path.abspath(self.folder_complete_path + "/" + ".ignore")
            ) as file_names:
                self.add_ignore_files(file_names)
        except:
            print("No ignored files")

        print(self.ignore_file_names)

    def init_meta_file(self):
        file_structure = []

        # Walk the tree of the directory and append a zipped stucture of directory and file names
        for (dirpath, dirnames, filenames) in walk(self.folder_complete_path):
            file_structure.append((dirpath, filenames))

        file_objects = []
        # Loop through each directory
        for folder in file_structure:
            folder_files = folder[1]  # Files in directory
            complete_folder_path = folder[0]  # Path of the directory

            # Loop through each file name in directory
            for file in folder_files:
                # If not part of the ignore files
                if file not in self.ignore_file_names:
                    print(file)
                    print(self.ignore_file_names)
                    # Compute the relative path of the file
                    paths = [
                        path.relpath(complete_folder_path, self.folder_relative_path),
                        file,
                    ]
                    relative_path_of_file = path.join(*paths)

                    # Make a File object out of it, see: dataStuctures.file
                    file_objects.append(
                        file_.File(
                            self.folder_complete_path,
                            relative_path_of_file,
                            self.uuid,
                            self.encoder,
                        )
                    )

        # Get all meta_data from each file in a list
        meta_data = {}
        for file in file_objects:
            meta_data.update(file.to_dict())

        self.write_to_meta_data_file(meta_data)

    def write_to_meta_data_file(self, data):
        # Open meta data
        meta_data_file = open(self.meta_data_path, "w")

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
            path_to_meta = path.join(self.folder_complete_path, "meta.json")
            file = open(path_to_meta, "r")

            self.meta_data = json.loads(file.read())
        except:
            print("meta does not exist")

    def update_file_meta_data(self, file_uuid, meta_data):
        self.load_meta_data()
        self.meta_data.update({file_uuid: meta_data})
        self.write_to_meta_data_file(self.meta_data)

    def get_node_meta_data(self):
        return {"UUID": str(self.uuid), "IP": self.ip, "SERVER_PORT": self.server_port}

    def accept_join_request(self, data):
        # If the network key matches
        response = {"SUCCESS": False}
        if data["NETWORK_KEY"] == self.network_key:
            print("Adding node to peers")
            self.add_peer(data["NODE_DATA"])
            self.add_uuid_to_worker(data["FILES"])

            self.load_meta_data()
            response.update(
                {
                    "SUCCESS": True,
                    "FILES": [file_uuid for file_uuid in self.meta_data.keys()],
                    "NODE_DATA": self.get_node_meta_data(),
                }
            )

            return response

        return response

    def add_peer(self, peer_data):
        if hasattr(self, 'peers'):
            self.peers = {}

        self.peers.update(
            {
                peer_data["UUID"]: {
                    "IP": peer_data["IP"],
                    "SERVER_PORT": peer_data["SERVER_PORT"],
                }
            }
        )

        print(self.peers)

    def fetch_file_meta_data(self, uuid_str):
        self.load_meta_data()
        return self.meta_data[uuid_str]

    def fetch_file(self, uuid_str):
        file_meta_data = self.fetch_file_meta_data(uuid_str)

        relative_file_path = file_meta_data["relative_path"]
        complete_file_path = path.join(self.folder_complete_path, relative_file_path)

        file = open(complete_file_path, "r")

        return file

    def add_file(self, file_uuid, meta_data, file_content):
        self.update_file_meta_data(file_uuid, meta_data)
        self.write_file_content(meta_data["relative_path"], file_content)

    def write_file_content(self, relative_path, file_content):
        file = open(path.join(self.folder_complete_path, relative_path), "w")
        file.write(file_content)
        file.close()

    def update_file_meta(self, file_uuid, updated_meta: dict):
        self.load_meta_data()
        file_meta_data = self.meta_data[file_uuid]

        for key in updated_meta.keys():
            file_meta_data.update({key: updated_meta[key]})

    def add_uuid_to_worker(self, file_uuids):
        for uuid in file_uuids:
            self.work_buffer.put({
                "FILE": uuid 
            })
        

class Client:
    def __init__(self, node: Node):
        self.node = node
        self.set_up_client_socket()
        self.file_watcher = Watcher(self.node.folder_complete_path)

    def set_up_client_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind((self.node.ip, self.node.client_port))

    def request_join_network(self, ip, port, network_key: int):
        self.node.load_meta_data()
        # Create join request
        request = {
            "type": "JOIN",
            "data": {
                "NETWORK_KEY": network_key,
                "FILES": [file_uuid for file_uuid in self.node.meta_data.keys()],
                "NODE_DATA": self.node.get_node_meta_data(),
            },
        }

        response = {}

        try:
            # Connect to node which in which this client wants to join
            self.client_socket.connect((ip, port))

            # Send join request
            data_transmitters.send_json(self.client_socket, request)

            # Recieve response
            response = data_transmitters.receive_json(self.client_socket)

            if response["SUCCESS"] == True:
                self.node.add_peer(response["NODE_DATA"])
                
            
            self.start_worker()

        except:
            traceback.print_exc()
            # self.client_socket.close()
            return None
        
    def request_file(self, file_uuid):
        request = {"type": "FILE", "data": {"uuid": file_uuid}}

        response = {}

    def start_worker(self):
        start_a_thread(self.wait_for_work)
    
    def start_watcher(self):
        start_a_thread(self.wait_for_file_update)

    def wait_for_work(self):
        # While true block for work
        while True:
            work = self.node.work_buffer.get(block=True)
            print(work)

    def wait_for_file_update(self):
        # While true block for file updates
        while True:
            update = self.file_watcher.event_queue.get(block=True)
            print(update)


class Server:
    def __init__(self, node: Node):
        self.node = node

        # List of possible request and the function to handle it
        self.REQUEST = {
            "JOIN": self.node.accept_join_request,
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
        while True:
            print("listening")
            # Listen for request
            self.request_socket.listen()
            # Accept connection
            connection, address = self.request_socket.accept()
            # Dispatch a new thread to carry out request
            start_a_thread(self.handle_request, (connection, address))

    def handle_request(self, connection, address):
        # Grab the request
        request = data_transmitters.receive_json(connection)
        self.echo_request(request)

        # Get the type of request
        type_of_request = request["type"]

        # Use the type to call the right function
        # Pass the data in the request to that function
        try:
            response = self.REQUEST[type_of_request](request["data"])
            print(response)
            # Send response back
            data_transmitters.send_json(connection, response)
        except:
            traceback.print_exc()
            print("REQUEST not set up yet")
            
    def echo_request(self, request):
        print(request)


def start_a_thread(function, args_=()):
    thread = threading.Thread(target=function, args=args_)
    thread.start()
