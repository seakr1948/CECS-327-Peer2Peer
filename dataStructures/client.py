import socket
from communication.data_transmitters import *

class Client:
    def __init__(self, port):
        self.port = port
        self.set_up_client_socket()

    def set_up_client_socket(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def send_request(self, data):
        """
        Sends a request given
        ip
        port
        request : must be packaged
        """
        ip = data["IP"]
        port = data["SERVER_PORT"]
        request = data
        try:
            # Try to send join request
            send_json(self.client_socket, request)

        except:
            # Reconnect and try again
            self.client_socket.connect((ip, port))
            send_json(self.client_socket, request)

        return self.client_socket

    def send_file(self, data):
        """
        Sends a request given
        ip
        port
        request : must be packaged
        """
        ip = data["IP"]
        port = data["SERVER_PORT"]

        file_buffer = data["FILE_CONTENT"]
        file_meta_data = data["META_DATA"]
        request = self.build_recv_file_request(file_meta_data)

        try:
            # Send join request
            send_file(self.client_socket, file_buffer, request)

        except:
            self.client_socket.connect((ip, port))
            send_file(self.client_socket, file_buffer, request)

        return self.client_socket

    def build_recv_file_request(file_meta):
        return {
            "TYPE": "RECV_FILE",
            "DATA": {
                "META_DATA": file_meta
            },
        }
    