# CECS-327-Peer2Peer
This is a file syncer acrross multiple linux machines. It is a distributed system design, and there is no limit to how many machines can join the network.

## Usage
`cooler_dropbox.py [-h] [--init_network] [--load] shared_folder server_port client_port`

positional arguments: <br />
  `shared_folder`   relative path of shared folder <br />
  `server_port`     port that listens for request  <br />
  `client_port`     port that broadcast changes  <br />

optional arguments: <br />
  `-h, --help`      show this help message and exit <br />
  `--init_network`  starts network <br />
  `--load`          loads meta file, otherwise init meta file <br />

## Overview of design
The architecture of the program was designed by Ruben Bramasco. https://github.com/Rv-ben
### Worker Thread
The design relies heavily on having a single worker thread in which all incoming/outgoing communication passes through. The worker thread is responsible in deciding which file the node needs, whether or not it needs to store an incoming file, where to store an incoming file, sending files to other nodes, etc. Every decision of the overall node is made by the worker thread, including which nodes are allowed to join the network.
### Server Thread
The server thread is responsible for recieving request/files and forwarding them to the worker thread via a buffer in the form of a Queue.
### Watcher Thread
The watcher thread is responsible for watching file changes on the repository and forwarding those updates to the worker thread. Where the worker thread will decide whether or not it needs to propagate the updates throughout the network.
### A helpful diagram
![image](https://user-images.githubusercontent.com/36426490/117511167-29dd3f80-af42-11eb-87a2-ab4ee3da5e7a.png)
