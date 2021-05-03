from os import path
from queue import Empty, LifoQueue
import threading
import uuid
from dataStructures.client import Client
from dataStructures.server import Server
from dataStructures.repo import Repo
from dataStructures.work_builder import *
from fileSystemHelpers.Watcher import Watcher
import traceback

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
        self.complete_path = path.abspath(shared_folder_relative_path)
        self.ip = ip
        self.server_port = server_port
        self.client_port = client_port
        self.encoder = [9, 4, 3, 6]
        self.network_key = network_key

        self.uuid = uuid
        self.peers = {}
        self.watcher = Watcher(self.complete_path)
        # Meta data path
        self.repo = Repo(self.folder_relative_path, self.uuid, self.watcher)

        # Work buffer for the client
        self.work_buffer = LifoQueue()
        self.client = Client(self.client_port)
        self.server = Server(self.ip, self.server_port)

        self.WORK = {
            "SEND_REQUEST": self.client.send_request,
            "SERVE_FILE": self.client.send_file,
            "FILE_REQUEST": self.handle_file_request,
            "FETCH_FILE": self.request_file,
            "RECV_FILE": self.handle_incoming_file,
            "JOIN": self.handle_join_request,
            "SEND_DELETE": self.send_delete,
            "DELETE": self.recv_delete
        }

        self.INCOMING_MAP = {
            "ADD": self.handle_file_add,
        }
    
    def get_node_meta_data(self):
        return {
            "UUID": str(self.uuid),
            "IP": self.ip,
            "SERVER_PORT": self.server_port,
        }

    def add_peer(self, peer_data):
        if hasattr(self, "peers"):
            self.peers = {}

        self.peers.update(
            {
                peer_data["UUID"]: {
                    "IP": peer_data["IP"],
                    "SERVER_PORT": peer_data["SERVER_PORT"],
                }
            }
        )

        print("PEERS: " + str(self.peers.keys()))

    def start_worker(self):
        start_a_thread(self.wait_for_work)

    def start_watcher(self):
        start_a_thread(self.wait_for_file_update)
    
    def start_server(self):
        self.server.set_up_request_socket()
    
    def start_request_transport(self):
        start_a_thread(self.push_request_buffer_to_work)

    def wait_for_work(self):
        # While true block for work
        while True:
            print("here")
            try:
                work = self.work_buffer.get(block=True)
                self.WORK[work["TYPE"]](work["DATA"])
                print("WORK: " + str(work))
            except:
                traceback.print_exc()
                print("WORK FAILED")
    
    def push_request_buffer_to_work(self):
        while True:
            request = self.server.request_buffer.get(block=True)
            self.work_buffer.put(request)

    def wait_for_file_update(self):
        # While true block for file updates
        while True:
            
            update = self.file_watcher.event_queue.get()
            print(update)

    def request_network_join(self, ip, port, network_key):
        self.repo.load_meta_data()
        data = {
            "TYPE": "JOIN",
            "DATA": {
                "IP": ip,
                "SERVER_PORT": port,
                "NETWORK_KEY": self.network_key,
                "FILES": list(self.repo.get_files()),
                "NODE_DATA": self.get_node_meta_data()
            },
        }
        self.client.send_request(data)

    def check_request_buffer(self):
        self.server.request_buffer.get()

    def add_uuid_to_worker(self, file_uuids, node_uuid):
        for uuid in file_uuids:
            print("Added file" + uuid)
            self.add_work_to_worker(
                {"TYPE": "FETCH_FILE", "DATA": {"FILE": uuid, "NODE": node_uuid}}
            )

    def add_work_to_worker(self, work):
        self.work_buffer.put(work)
    
    def handle_join_request(self, data):
        if (
            data["NETWORK_KEY"] == self.network_key
            and data["NODE_DATA"]["UUID"] not in self.peers
        ):  
            self.add_peer(data["NODE_DATA"])
            network_key = data["NETWORK_KEY"]
            file_meta_data = self.repo.get_files()
            node_meta_data = self.get_node_meta_data()
            work = {
                "TYPE": "SEND_REQUEST",
                "DATA": {
                    "TYPE": "JOIN",
                    "DATA": {
                        "IP": data["NODE_DATA"]["IP"],
                        "SERVER_PORT": data["NODE_DATA"]["SERVER_PORT"],
                        "FILES": list(self.repo.get_files()),
                        "NODE_DATA": self.get_node_meta_data(),
                        "NETWORK_KEY": self.network_key
                    }
                }
            }
            self.add_work_to_worker(work)
            self.handle_network_accept(data)
    
    def handle_network_accept(self, data):
        self.add_peer(data["NODE_DATA"])
        self.add_uuid_to_worker(data["FILES"], data["NODE_DATA"]["UUID"])
    
    def request_file(self, data):
        node_id = data["NODE"]
        data = {
            "TYPE": "FILE_REQUEST",
            "DATA": {
                "IP": self.peers[node_id]["IP"],
                "SERVER_PORT": self.peers[node_id]["SERVER_PORT"],
                "FILE": data["FILE"], 
                "NODE": str(self.uuid)},
        }

        self.client.send_request(data)

    def handle_file_request(self, data):
        file_id = data["FILE"]
        node_id = data["NODE"]
        ip = data["IP"]
        port = data["SERVER_PORT"]
        type_ = "ADD"

        file_meta_data = self.repo.fetch_file_data(file_id)
        file_buffer = self.repo.fetch_file(file_id)

        work = build_serve_file_work(file_id, file_meta_data, file_buffer, node_id, ip, port, type_)

        self.add_work_to_worker(work)

    def handle_incoming_file(self, data):
        print(data)
        self.INCOMING_MAP[data["F_TYPE"]](data)

    def handle_file_add(self, data):
        file_id = data["FILE"]
        file_data = data["META_DATA"]
        file_content_bytes = data["FILE_CONTENT"]
        self.repo.add_file(file_id, file_data, file_content_bytes)

    def send_delete(self, data):
        for peer in self.peers:
            request = {
                "TYPE": "DELETE",
                "DATA": {
                    "IP": peer["IP"],
                    "SERVER_PORT": peer["SERVER_PORT"],
                    "FILE": data["FILE"],
                    "SIGS": [str(self.uuid)]
                },
            }
            self.client.send_request(request)
    
    def recv_delete(self, data):
        if str(self.uuid) not in data["SIGS"]:
            data["SIGS"].append(str(self.uuid))
            
            # Delete repo file HERE
            for peer in self.peers:
                self.client.send_request({
                    "TYPE": "DELETE",
                    "DATA": {
                        "IP": peer["IP"],
                        "SERVER_PORT": peer["SERVER_PORT"],
                        "FILE": data["FILE"],
                        "SIGS": data["SIGS"]
                    }
                })
    
    def send_file_update(self, data):
        file_id = data["FILE"]
        type_ = "UPDATE"
        Sigs = [str(self.uuid)]
        for peer in self.peers:
            file_meta_data = self.repo.fetch_file_data(file_id)
            file_buffer = self.repo.fetch_file(file_id)
            node_id = "some_Data"
            ip = peer["IP"]
            port = peer["SERVER_PORT"]

            work = build_serve_file_work(file_id, file_meta_data, file_buffer, node_id, ip, port, type_, Sigs)

            self.add_work_to_worker(work)

    def handle_incoming_update(self, data):
        
        pass
    
    def watcher_dispatcher(self, event_token):
        repo.load_meta_data()
        meta_file = repo.meta_data

        for key in meta_file:
            if key["relative_path"] == event_token["PATH_SRC"]:
                uuid = key
        
        event = event_token["EVENT_TYPE"]
        
        return (uuid, event)
        



def start_a_thread(function, args_=()):
    thread = threading.Thread(target=function, args=args_)
    thread.start()