import socket
import threading
from queue import Queue
import time

class FindPorts:
    def __init__(self):
        self.target = ''
        self.openPorts = []
        self.q = Queue()
        self.printLock = threading.Lock()

    #return the open ports
    def get_open_ports(self):
        return self.openPorts

    #scans an individual port
    def pscan(self,port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:    #try to connect to port, if able print to console and add it to current open ports
            con = s.connect((self.target,port))
            with self.printLock:
                print('port',port,'is open!')
            self.openPorts.append(port)
            con.close()
        except:
            pass
    
    #function that the threads will be working on
    def threader(self):
        while True:
            worker = self.q.get()
            self.pscan(worker)
            self.q.task_done()

    #function that will scan for ports on a parameter IP
    def scan_for_ports(self, ip):
        self.target = ip
        self.openPorts = [] #reset the openPorts list to be blank to not interfere with previous scan_for_ports

        for x in range (20): #number of threads
            t = threading.Thread(target = self.threader)
            t.daemon = True #thread will be killed when tasks are done
            t.start()

        for worker in range(8000,8101): #range of ports we are scanning for
            self.q.put(worker)

        self.q.join()   #wait for all threads to catch up

def main():
    myFinder = FindPorts()
    myFinder.scan_for_ports('47.154.12.183')
    ports = myFinder.get_open_ports()

    print(ports)

if __name__ == "__main__":
    main()
