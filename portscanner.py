import socket

hostname = socket.gethostname()
print(hostname)

ip_add = socket.gethostbyname(hostname)

print(ip_add)