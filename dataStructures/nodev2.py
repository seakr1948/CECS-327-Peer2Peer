from queue import LifoQueue
import uuid
from dataStructures.client import Client
from dataStructures.server import Server
from dataStructures.repo import Repo

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
        self.repo = Repo(self.folder_relative_path)

        # Work buffer for the client
        self.work_buffer = LifoQueue()
        self.client = Client(self.client_port)
        self.server = Server(self.ip, self.server_port)

        self.WORK = {
            "SEND_REQUEST": self.client.send_request,
            "SERVE_FILE": self.client.send_file,
            "FETCH_FILE": self.request_file,
            "DELETE_FILE": pass,
            "RECV_FILE": pass,
            "ADD_FILE": pass,
            "JOIN": pass 
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
                    print("WORK: " + str(work))
                    self.WORK[work["TYPE"]](work["DATA"])
                except:
                    #self.work_buffer.put(work)
                    print("Failed work")

        def wait_for_file_update(self):
            # While true block for file updates
            while True:
                update = self.file_watcher.event_queue.get(block=True)
                print(update)


def start_a_thread(function, args_=()):
    thread = threading.Thread(target=function, args=args_)
    thread.start()