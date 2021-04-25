import json
from sys import meta_path
import uuid

from os import path
from os import walk

import dataStructures.file as file_

class node:
    
    def __init__(self, shared_folder_relative_path: str, ip: str, port_number: str):

        self.folder_relative_path = shared_folder_relative_path
        self.folder_complete_path = path.abspath(self.folder_relative_path)
        self.ip = ip
        self.port_number = port_number
        self.encoder = [9,4,3,6]
    
    def __str__(self):
        return str(self.uuid) + "\n" + str(self.peers)

    def init_network(self):

        self.uuid = uuid.uuid4()
        self.peers = {}

    def join_network(self, peers: dict, uuid_: uuid.UUID):

        self.peers = dict(peers)
        self.uuid = uuid.UUID(str(uuid_))
    
    def accept_join_request(self):

        peers_minus_joining_node = dict(self.peers)
        peers_minus_joining_node.update({self.uuid: "data"})
        joining_node_uuid = uuid.uuid4()

        self.peers.update({joining_node_uuid: "data"})

        return peers_minus_joining_node, joining_node_uuid
    
    def init_meta_file(self):
        files = []

        for (dirpath, dirnames, filenames) in walk(self.folder_complete_path):
            files.extend(filenames)

        file_objects = [
            file_.File(self.folder_relative_path + "/"+file_name, self.uuid, self.encoder)
            for file_name in files
            ]

        json_file = open(self.folder_complete_path + "/meta.json", 'w')

        list_of_meta_data = []
        for file in file_objects:
            list_of_meta_data.append(file.to_dict())
        
        json.dump(list_of_meta_data, json_file, indent=4, separators=(", ", ": "), sort_keys=True)
        json_file.close()
    
    def load_meta_data(self):

        try:
            file = open(self.folder_complete_path + '/meta.json', 'r')

            self.meta_data = json.load(file.read())
            print(self.meta_data)
        except:
            print("meta does not exist")

    def test_uuid(self):
        self.uuid = uuid.uuid4()