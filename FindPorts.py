import socket
import threading
from queue import Queue
import time

printLock = threading.Lock()
q = Queue()
target = ['']
openPorts = []

def setTarget(ip):
    target[0] = ip

def pscan(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        con = s.connect((target[0],port))
        with printLock:
            print('port',port,'is open!')
        openPorts.append(port)
        con.close()
    except:
        pass

def threader():
    while True:
        worker = q.get()
        pscan(worker)
        q.task_done()

def scanForPorts():
    openPorts = []
    for x in range (20):
        t = threading.Thread(target = threader)
        t.daemon = True
        t.start()

    for worker in range(8000,8101):
        q.put(worker)

    q.join()


start = time.time()
print("My IP")
setTarget('47.154.12.183')
scanForPorts()
print('done')
print("---%s seconds---" % (time.time() - start))

print(openPorts)