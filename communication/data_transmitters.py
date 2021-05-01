import socket
import json


def receive_json(connection):

    with connection:
        try: 
            data_recieved = connection.recv(1024)
        except:
            return None

    return dict(json.loads(data_recieved))


def send_json(connection, message):

    with connection:

        try: 

            # Deserialize JSON and sent it to the server
            json_string = json.dumps(message)

            # Convert to bytes
            json_to_bytes = json_string.encode("utf-8")
            connection.send(json_to_bytes)
        except:
            return None
