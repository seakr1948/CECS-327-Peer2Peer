import socket
import json

def send_json(host, port, jsonObj):
    data_recieved = {}
    # Create a new socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_socket:

        # Bind Socket to the correct address and port
        temp_socket.bind((host, port))

        # Deserialize JSON and sent it to the server
        jsonString = json.dumps(jsonObj)
        temp_socket.sendall(jsonString)

        print("Sent this : " + str(jsonObj))
    
    # Closes automatically

def receive_json(host, port):

    # Wait for request
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:

        print("Listening...")
        print("IP: " + host)
        print("Port: "+ str(port))
        server_socket.bind((host, port))
        server_socket.listen()

        connection, address = server_socket.accept()

        with connection:
            print("Connected to: ", address)
            data_recieved = connection.recv(1024)
            print(data_recieved)
        
        connection.close()
    
    socket.close()
    return data_recieved
