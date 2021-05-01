import json
from socket import socket
import uuid
import dataStructures.file as file_
import communication.data_transmitters as data_transmitters
import logging
import threading

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
    ):

        # Standard node data
        self.folder_relative_path = shared_folder_relative_path
        self.folder_complete_path = path.abspath(self.folder_relative_path)
        self.ip = ip
        self.server_port = server_port
        self.client_port = client_port
        self.encoder = [9, 4, 3, 6]
        self.network_key = network_key
        
        # Work buffer for the client
        self.work_buffer = LifoQueue()
        self.client = Client(self)
        self.server = Server(self)
        
    def __str__(self):
        return str(self.uuid) + "\n" + str(self.peers)

    def init_network(self):

        # Init a uuid for this node
        self.uuid = uuid.uuid4()
        # Starts a dict of peers
        self.peers = {}

        try:
            self.ignore_file_names = []
            with open(path.abspath(self.folder_complete_path + "/" + ".ignore")) as f:
                for file_name in f:
                    self.ignore_file_names.append(file_name.strip("\n"))
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
            folder_files = folder[1] # Files in directory
            complete_folder_path = folder[0]  # Path of the directory

            # Loop through each file name in directory
            for file in folder_files:
                # If not part of the ignore files
                if file not in self.ignore_file_names:
                    # Compute the relative path of the file
                    paths = [
                        self.folder_relative_path,
                        path.relpath(complete_folder_path, self.folder_relative_path),
                        file,
                    ]
                    relative_path_of_file = path.join(*paths)
                    
                    # Make a File object out of it, see: dataStuctures.file
                    file_objects.append(
                        file_.File(relative_path_of_file, self.uuid, self.encoder)
                    )

        # Open a new meta file
        json_file = open(self.folder_complete_path + "/meta.json", "w")

        # Get all meta_data from each file in a list
        list_of_meta_data = {}
        for file in file_objects:
            list_of_meta_data.update(file.to_dict())

        # Make a jsonstring out of the data and write to the file 
        json.dump(
            list_of_meta_data,
            json_file,
            indent=4,
            separators=(", ", ": "),
            sort_keys=True,
        )
        # Close file
        json_file.close()

    def load_meta_data(self):

        try:
            file = open(self.folder_complete_path + "/meta.json", "r")

            self.meta_data = json.load(file.read())
            print(self.meta_data)
        except:
            print("meta does not exist")

    def get_node_meta_data(self):
        return {"UUID": self.uuid(), "IP": self.ip, "REQUEST_PORT": self.request_port}

    def accept_join_request(self, data):
        # If the network key matches
        if data["key"] == self.network_key:
            print("Adding node to peers")
            new_node_uuid = uuid.uuid4()
            self.peers.update({new_node_uuid: data})

            return True
        
        return False
            
        
class Client:

    def __init__(self, node: Node):
        self.node = node
        #self.set_up_client_socket()

    def set_up_client_socket(self):
        self.client_socket = socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.bind((self.node.ip, self.node.client_port))

    def request_join_network(self, ip, port, network_key: int):
        # Create join request
        request = {
            "type": "JOIN",
            "data": {
                "key": network_key,
                "ip": self.node.ip,
                "Request_port": self.node.server_port,
            },
        }

        response = {}

        try:
            # Connect to node which in which this client wants to join
            self.client_socket.connect((ip, port))
            
            # Send join request
            data_transmitters.send_json(self.client_socket, request)
            # Listen for repsonse
            self.client_socket.listen()
            # Recieve data
            response  = data_transmitters.receive_json(self.client_socket)

        except:
            print("Something went wrong during join request")
            return None
        
        return response
    
    def wait_for_work(self):
        # While true block for work
        while True:
            work = self.node.work_buffer.get(block=True)
        
class Server:

    def __init__(self, node: Node):
        self.node = node

        # List of possible request and the function to handle it
        self.REQUEST = {
            "JOIN" : self.node.accept_join_request
        }

    def start_server(self):
        # Start listening for request
        self.set_up_request_socket()

    def set_up_request_socket(self):
        # Create a new socket and bind it to the node IP
        self.request_socket = socket(socket.AF_INET, socket.SOCK_STREAM)
        self.request_socket.bind((self.node.ip, self.node.server_port))
        # Start request dispatching
        start_a_thread(self.dispatch_request)

    def dispatch_request(self):
        while True:
            # Listen for request
            self.request_socket.listen()
            # Accept connection
            connection, address = self.request_socket.accept()
            # Dispatch a new thread to carry out request
            start_a_thread(self.handle_request, (connection, address))

    def handle_request(self, connection, address):
        # Grab the request
        request = data_transmitters.receive_json(connection, address)
        
        # Get the type of request
        type_of_request = request["type"]

        # Use the type to call the right function
        # Pass the data in the request to that function
        success = self.REQUEST[type_of_request](request["data"])

        # Build response
        response = {"success": success}
        
        # Send response back
        data_transmitters.send_json(connection, response)
        
        # Close connection
        connection.close()

def start_a_thread(self, function, args_=()):
        thread = threading.Thread(target=function, args=args_)
        thread.start()
