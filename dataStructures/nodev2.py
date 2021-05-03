from queue import Empty, LifoQueue
import threading
import uuid
from dataStructures.client import Client
from dataStructures.server import Server
from dataStructures.repo import Repo
from dataStructures.work_builder import *
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
        self.ip = ip
        self.server_port = server_port
        self.client_port = client_port
        self.encoder = [9, 4, 3, 6]
        self.network_key = network_key

        self.uuid = uuid
        self.peers = {}

        # Meta data path
        self.repo = Repo(self.folder_relative_path, self.uuid)

        # Work buffer for the client
        self.work_buffer = LifoQueue()
        self.client = Client(self.client_port)
        self.server = Server(self.ip, self.server_port)

        self.WORK = {
            "SEND_REQUEST": self.client.send_request,
            "SERVE_FILE": self.client.send_file,
            "FETCH_FILE": self.request_file,
            "RECV_FILE": self.handle_file_add,
            "JOIN": self.handle_join_request
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
            "IP": ip,
            "SERVER_PORT": port,
            "DATA": build_join_request(network_key, self.repo.meta_data, self.get_node_meta_data()),
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
            network_key = data["NETWORK_KEY"]
            file_meta_data = self.repo.get_files()
            node_meta_data = self.get_node_meta_data()
            work = build_join_work(network_key, file_meta_data, node_meta_data)
            print(work)
            self.add_work_to_worker(work)
            self.handle_network_accept(data)
    
    def handle_network_accept(self, data):
        self.add_peer(data["NODE_DATA"])
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

        file_meta_data = self.repo.fetch_file_data(file_id)
        file_buffer = self.repo.fetch_file(file_id)

        work = build_serve_file_work(file_id, file_meta_data, file_buffer, node_id)

        self.add_work_to_worker(work)

    def handle_file_add(self, data):
        file_id = data["FILE"]
        file_data = data["META_DATA"]
        file_content_bytes = data["FILE_CONTENT"]
        self.repo.add_file(file_id, file_data, file_content_bytes)
    


def start_a_thread(function, args_=()):
    thread = threading.Thread(target=function, args=args_)
    thread.start()