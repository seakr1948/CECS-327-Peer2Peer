from io import BytesIO, FileIO
import socket
import json
import traceback

MESSAGE_LENGTH = 2048


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
        print(data)
        unpadded_message = unpad_message(data)
        print(unpadded_message + "<- \n\n")
        return dict(json.loads(unpadded_message))
    except:
        return None

def recv_all(connection: socket.socket, size):
    return connection.recv(size, socket.MSG_WAITALL)


def send_json(connection: socket.socket, message):

    # Deserialize JSON and sent it to the server
    json_string = json.dumps(message)
    json_string = pad_message(json_string)
    # Convert to bytes
    json_to_bytes = json_string.encode("utf-8")
    connection.sendall(json_to_bytes)


def send_file(connection: socket.socket, file: BytesIO, meta_data, header):
    meta_data.update({"BUFFER_SIZE": file.getbuffer().nbytes})
    send_json(connection, header)
    connection.recv(1)
    send_json(connection, meta_data)
    connection.recv(1)

    connection.send(file.read(meta_data["BUFFER_SIZE"]))

def receive_file(connection: socket.socket):

    print(connection.send(bytes('t')))
    meta_data = receive_json(connection)
    file_size = meta_data["BUFFER_SIZE"]
    file_buffer = BytesIO()

    print(connection.send(bytes('t')))

    file = recv_all(connection, file_size)
    print(file + " <--")
    print(file.decode() + "<---")
    file_buffer.write(file)
    
    return meta_data, file_buffer
    


if __name__ == "__main__":

    message = "{ 'test' : True }"

    print(len(message.encode("utf-8")))

    print(unpad_message(pad_message(message)))