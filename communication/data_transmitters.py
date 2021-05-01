import socket
import json


def receive_json(connection):

    with connection:
        data_recieved = connection.recv(1024)

    return dict(json.loads(data_recieved))


def send_json(connection, message):

    with connection:

        # Deserialize JSON and sent it to the server
        json_string = json.dumps(message)

        # Convert to bytes
        json_to_bytes = json_string.encode("utf-8")
        connection.send(json_to_bytes)
