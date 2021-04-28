import socket
import time

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('', 8087))
serversocket.listen(5)

connection, address = serversocket.accept()

b = connection.recv(1)
time.sleep(0.1)
serversocket.close()
connection.shutdown(socket.SHUT_WR)
connection.close()
print(b)