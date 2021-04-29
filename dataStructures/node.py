import json
import uuid
import dataStructures.file as file_
import communication.dataRecievers as data_recievers
import logging
import threading

from os import path
from os import walk


class Node:
    def __init__(
        self,
        shared_folder_relative_path: str,
        ip: str,
        request_port: str,
        network_key=9999,
    ):

        self.folder_relative_path = shared_folder_relative_path
        self.folder_complete_path = path.abspath(self.folder_relative_path)
        self.ip = ip
        self.request_port = request_port
        self.encoder = [9, 4, 3, 6]

        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    def __str__(self):
        return str(self.uuid) + "\n" + str(self.peers)

    def init_network(self):

        self.uuid = uuid.uuid4()
        self.peers = {}

        try:
            self.ignore_file_names = []
            with open(path.abspath(self.folder_complete_path + "/" + ".ignore")) as f:
                for file_name in f:
                    self.ignore_file_names.append(file_name.strip("\n"))
        except:
            print("No ignored files")

        print(self.ignore_file_names)

    def join_network(self, accepting_node: dict, uuid_: uuid.UUID):

        accepting_node_uuid = accepting_node["UUID"]
        self.peers = {accepting_node_uuid: accepting_node}
        self.uuid = uuid.UUID(str(uuid_))

    def accept_join_request(self, ip, port_number):
        joining_node_uuid = uuid.uuid4()
        self.peers.update({joining_node_uuid: "data"})

        return peers_minus_joining_node, joining_node_uuid

    def request_join_network(self, ip, port, network_key: int):
        request = {
            "type": "JOIN",
            "params": {
                "key": network_key,
                "ip": self.ip,
                "Request_port": self.request_port,
            },
        }

        self.start_a_thread(
            data_recievers.send_json,
            args_=(
                ip,
                port,
                request,
            ),
        )

    def init_meta_file(self):
        file_structure = []

        for (dirpath, dirnames, filenames) in walk(self.folder_complete_path):
            file_structure.append((dirpath, filenames))

        file_objects = []
        for folder in file_structure:
            folder_files = folder[1]
            for file in folder_files:
                if file not in self.ignore_file_names:
                    complete_folder_path = folder[0]
                    paths = [
                        self.folder_relative_path,
                        path.relpath(complete_folder_path, self.folder_relative_path),
                        file,
                    ]
                    relative_path_of_file = path.join(*paths)
                    print(relative_path_of_file)
                    file_objects.append(
                        file_.File(relative_path_of_file, self.uuid, self.encoder)
                    )

        json_file = open(self.folder_complete_path + "/meta.json", "w")

        list_of_meta_data = []
        for file in file_objects:
            list_of_meta_data.append(file.to_dict())

        json.dump(
            list_of_meta_data,
            json_file,
            indent=4,
            separators=(", ", ": "),
            sort_keys=True,
        )
        json_file.close()

    def load_meta_data(self):

        try:
            file = open(self.folder_complete_path + "/meta.json", "r")

            self.meta_data = json.load(file.read())
            print(self.meta_data)
        except:
            print("meta does not exist")

    def start_a_thread(self, function, args_= ()):
        listen_for_request_thread = threading.Thread(target=function, args=args_)
        listen_for_request_thread.start()

    def listen_for_request(self):
        print(data_recievers.receive_json(self.ip, self.request_port))

    def get_node_meta_data(self):
        return {"UUID": self.uuid(), "IP": self.ip, "REQUEST_PORT": self.request_port}

    def test_uuid(self):
        self.uuid = uuid.uuid4()
