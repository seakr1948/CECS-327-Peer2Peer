from io import BytesIO, FileIO
import socket
import json
import traceback


def receive_json(connection):

    try:
        data_recieved = connection.recv(1024)
        data_recieved_string = data_recieved.decode('utf-8')
    except:
        traceback.print_exc()
        return None

    return dict(json.loads(data_recieved_string))


def send_json(connection, message):

    # Deserialize JSON and sent it to the server
    json_string = json.dumps(message)
    # Convert to bytes
    json_to_bytes = json_string.encode("utf-8")
    connection.send(json_to_bytes)


def send_file(connection: socket.socket, file: BytesIO, meta_data, header):

    send_json(connection, header)
    send_json(connection, meta_data)

    l = file.read(1024)
    while l:
        connection.send(l)
        l = file.read(1024)

def receive_file(connection: socket.socket):

    meta_data = receive_json(connection)
    file_buffer = BytesIO()

    l = connection.recv(1024)
    while l:
        file_buffer.write(l)
        l = connection.recv(1024)
    
    return meta_data, file_buffer
    


