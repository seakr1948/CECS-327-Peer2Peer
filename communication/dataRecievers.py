import socket
import json

def send_json(host, port, jsonObj):

    # Create a new socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:

        # Bind Socket to the correct address and port
        temp_socket.bind((host, port))

        # Deserialize JSON and sent it to the server
        jsonString = json.dumps(jsonObj)
        socket.sendall(jsonString)

        print("Sent this : " + str(jsonObj))
    
    # Closes automatically

def receive_json(host, port):

    # Wait for request
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        print("Listening...")
        server_socket.bind((host, port))
        server_socket.listen()

        connection, address = server_socket.accept()

        with connection:
            print("Connected to: ", address)
            data_recieved = connection.recv()
            print(data_recieved)
        
        # Closes automatically
        return data_recieved
