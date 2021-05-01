import socket
import time
import json

def receiveFile(filename, socket: socket):
    # This sets up the file manipulation 
    # (In this case it will write the file 
    # that is being sent from the client)
    file = open('./test_folder/{}'.format(filename), 'wb')

    # data_recieved is a buffer that gets pieces of the file
    data_recieved = socket.recv(1024)

    #while loop that continues to write the file until 
    # there is no more of the file to write
    while data_recieved:
        #writes recieved data to the file
        file.write(data_recieved)
        # looks for more data
        data_recieved = socket.recv(2014)
    # Once there is no more data the while loop is exited
    # close the file to stop writing to it
    file.close()

print("File recieved")

host = ""
port = 5000

print (socket.gethostname())

mysocket = socket.socket()
mysocket.bind((host, port))

mysocket.listen(1)
conn, addr = mysocket.accept()
print("Connection from: " + str(addr))


receiveFile("input.jpg",conn)

print("File recieved")

conn.close()
print("Closing connection...")

#code to deserialize JSON data from client. Will return a JSON object
# def recvJson():
#     recievedJson = data
#     jsonObj = json.loads(recievedJson) #deserializing JSON data sent from client
#     return jsonObj
