import socket
import time

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('192.168.56.1', 8087))

clientsocket.send(b'a')
time.sleep(0.05)
clientsocket.close()