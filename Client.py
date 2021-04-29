import socket
import json

host = "DESKTOP-Q6J99TN"
port = 5000

mysocket = socket.socket()
mysocket.connect((host, port))

message = input(" -> ")

while message != "q":
    mysocket.send(message.encode())
    data = mysocket.recv(1024).decode()

    print("recieved from server: " + data)
    message = input(" -> ")

mysocket.close()

# take a JSON object and serializes it into a string which will be sent to the server
def sendJson(jsonObj):
    jsonString = json.dumps(
        jsonObj
    )  # serializing/marshalling the json data into a python string
    mysocket.sendall(jsonString)
