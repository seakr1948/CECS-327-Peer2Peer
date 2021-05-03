import socket
from communication.data_transmitters import *
import threading
from queue import LifoQueue

class Server:
    def __init__(self, ip, port):
        # List of possible request and the function to handle it
        self.request_buffer = LifoQueue()
        self.port = port
        self.ip = ip

    def set_up_request_socket(self):
        # Create a new socket and bind it to the node IP
        self.request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.request_socket.bind((self.ip, self.port))
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

    def handle_request(self, connection):
        while True:
            # Grab the request
            request = receive_json(connection)
            self.echo_request(request)

            recv_flag = False
            try:
                # Get the type of request
                type_of_request = request["TYPE"]
            except:
                print("Request not found")
            type_of_request = request["TYPE"]
            if type_of_request == "RECV_FILE":
                self.recv_file(connection, request)
                recv_flag = True
                continue

            # Use the type to call the right function
            # Pass the data in the request to that function
            if recv_flag == False:
                print("NON RECV REQUEST")
                self.request_buffer.put(request)
            # traceback.print_exc()

        connection.close()

    def recv_file(self, connection, request):
        try:
            meta_data = request["DATA"]["FILE_DATA"]["META_DATA"]
            file_id = request["DATA"]["FILE_DATA"]["FILE"]

            file_buffer = receive_file(connection, meta_data)
            data = {
                "META_DATA": meta_data, 
                "FILE": file_id,
                "FILE_CONTENT": file_buffer,
            }
            new_request = {
                "TYPE": "RECV_FILE",
                "DATA": data
            }
            self.request_buffer.put(new_request)
        except:
            print("Failed to get file")

    def serve_file(self, connection):
        pass

    def echo_request(self, request):
        print(request)


def start_a_thread(function, args_=()):
    thread = threading.Thread(target=function, args=args_)
    thread.start()
