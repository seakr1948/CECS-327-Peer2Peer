import node
import socket

if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())

    test_node = node.node("./test_folder", ip, "5555")
    test_node_2 = node.node("./test_folder", ip, "5555")
    test_node_3 = node.node("./test_folder", ip, "5555")

    test_node.init_network()

    peers, uuid = test_node.accept_join_request()
    
    test_node_2.join_network(peers, uuid)

    peers, uuid = test_node_2.accept_join_request()

    test_node_3.join_network(peers, uuid)



    #print(test_node)
    print(test_node_2)
    print(test_node_3)