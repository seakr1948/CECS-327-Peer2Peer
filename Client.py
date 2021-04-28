import socket

host = "DESKTOP-Q6J99TN"
port = 5000

mysocket = socket.socket()
mysocket.connect((host, port))

message = input(" -> ")

while message != 'q':
    mysocket.send(message.encode())
    data = mysocket.recv(1024).decode()

    print("recieved from server: " + data)
    message = input(" -> ")

mysocket.close()