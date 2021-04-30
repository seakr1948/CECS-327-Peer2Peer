import socket
import time

host = "0.0.0.0"
port = 5000

print (socket.gethostname())

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
