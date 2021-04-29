import socket
import time
import json

host = "0.0.0.0"
port = 5000

print (socket.gethostname())

mysocket = socket.socket()
mysocket.bind((host, port))

mysocket.listen(1)

conn, addr = mysocket.accept()
print("Connection from: " + str(addr))
while True:
    data = conn.recv(1024).decode()
    if not data:
        break
    print("from connected user: " + str(data))

    data = str(data).upper()
    print("sending: " + str(data))
    conn.send(data.encode())

conn.close()

#code to deserialize JSON data from client. Will return a JSON object
def recvJson():
    recievedJson = data
    jsonObj = json.loads(recievedJson) #deserializing JSON data sent from client
    return jsonObj