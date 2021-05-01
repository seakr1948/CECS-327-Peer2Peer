import socket
import json


def sendFile(filename, socket: socket):
    file = open(filename, 'rb')
    filedata = file.read(1024)

    while filedata:
        socket.send(filedata)
        filedata = file.read(1024)

    print("file sent!")


host = "DESKTOP-Q6J99TN"
port = 5000

mysocket = socket.socket()
mysocket.connect((host, port))

# message = input(" -> ")

print("sending file...")
sendFile("twitter-logo-small.jpg", mysocket)




# while message != 'q':
#     mysocket.send(message.encode())
#     data = mysocket.recv(1024).decode()

#     print("recieved from server: " + data)
#     message = input(" -> ")

print("connection closing...")
mysocket.close()

#take a JSON object and serializes it into a string which will be sent to the server
def sendJson(jsonObj):
    jsonString = json.dumps(jsonObj) #serializing/marshalling the json data into a python string
    mysocket.sendall(jsonString)