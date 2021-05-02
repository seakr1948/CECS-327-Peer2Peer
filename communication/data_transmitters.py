import socket
import json
import traceback


def receive_json(connection):

    try:
        data_recieved = connection.recv(1024)
    except:
        traceback.print_exc()
        return None

    return dict(json.loads(data_recieved))


def send_json(connection, message):

    # Deserialize JSON and sent it to the server
    json_string = json.dumps(message)
    print(message)
    # Convert to bytes
    json_to_bytes = json_string.encode("utf-8")
    connection.send(json_to_bytes)
    print(connection)


# 
def send_file(connection: socket.socket, file_contents = []):

    for i in file_contents:
        connection.send(i)

def receive_file(connection: socket.socket):

    received_data = connection.recv(1024)
    temp = []
    while received_data:
        temp.append(received_data)
        received_data = connection.recv(1024)

    return temp
