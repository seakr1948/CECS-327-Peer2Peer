from io import BytesIO, FileIO
import socket
import json
import traceback
from typing import BinaryIO

MESSAGE_LENGTH = 1024


def pad_message(message: str):
    current_length = len(message.encode("utf-8"))
    padding_needed = MESSAGE_LENGTH - current_length
    for i in range(padding_needed):
        message += ' '
    return message

def unpad_message(message: str):
    return message.strip(' ')

def receive_json(connection: socket.socket):

    try:
        data_recieved = recv_all(connection, MESSAGE_LENGTH)
        data = data_recieved.decode('utf-8')
        unpadded_message = unpad_message(data)
        return dict(json.loads(unpadded_message))
    except:
        return None

def recv_all(connection: socket.socket, size):
    data = bytearray()
    while len(data) < size:
        packet = connection.recv(size - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def send_json(connection: socket.socket, message):

    # Deserialize JSON and sent it to the server
    json_string = json.dumps(message)
    json_string = pad_message(json_string)
    # Convert to bytes
    json_to_bytes = json_string.encode("utf-8")
    connection.sendall(json_to_bytes)


def send_file(connection: socket.socket, file: BytesIO, header):
    send_json(connection, header)
    connection.recv(1).decode()
    connection.send(file.read())

def receive_file(connection: socket.socket, meta_data):
    connection.send('1'.encode('utf-8'))
    file_size = meta_data["file_size"]
    file = recv_all(connection, file_size)
    file.decode()
    file_buffer = BytesIO(file)
    
    return file_buffer
    


if __name__ == "__main__":

    message = "{ 'test' : True }"

    print(len(message.encode("utf-8")))

    print(unpad_message(pad_message(message)))