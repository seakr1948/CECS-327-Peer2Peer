import uuid

class node:
    
    def __init__(self, shared_folder_path: str, ip: str, port_number: str):

        self.shared_folder_path = shared_folder_path
        self.ip = ip
        self.port_number = port_number
    
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
        