import socket
import time
import json

host = "0.0.0.0"
port = 5000

print(socket.gethostname())

mysocket = socket.socket()
mysocket.bind((host, port))

mysocket.listen(1)
conn, addr = mysocket.accept()
print("Connection from: " + str(addr))

with open('image.jpg', 'wb') as file:

    while True:
        
        l = conn.recv(1024)

        if not (l):
            break
        
        file.write(l)
        
    file.close()
    print("Server stopping")
    conn.close()
conn.close()

# code to deserialize JSON data from client. Will return a JSON object
def recvJson():
    recievedJson = data
    jsonObj = json.loads(recievedJson)  # deserializing JSON data sent from client
    return jsonObj
