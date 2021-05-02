from io import BytesIO, FileIO
import socket
import json
import traceback

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
        data_recieved = connection.recv(250)
        data = data_recieved.decode('UTF-8')
        print(data)
    except:
        traceback.print_exc()
        return None

    return dict(json.loads(data))


def send_json(connection: socket.socket, message):

    print(message)
    connection.send()
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
    file_size = meta_data["file_size"]
    file_buffer = BytesIO()

    chunks_receieved = 1024
    l = connection.recv(1024)
    while chunks_receieved < file_size:
        file_buffer.write(l)
        l = connection.recv(1024)
        chunks_receieved += 1024
    
    return meta_data, file_buffer
    


if __name__ == "__main__":

    message = "{ 'test' : True }"

    print(len(message.encode("utf-8")))

    print(unpad_message(pad_message(message)))