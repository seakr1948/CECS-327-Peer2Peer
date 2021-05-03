
def build_join_request(network_key, file_meta_data, node_meta_data):
    return {
        "TYPE": "JOIN",
        "IP": node_meta_data["IP"],
        "SERVER_PORT": node_meta_data["SERVER_PORT"],
        "DATA": {
            "NETWORK_KEY": network_key,
            "FILES": [file_uuid for file_uuid in file_meta_data],
            "NODE_DATA": node_meta_data,
        },
    }

def build_work(type, data):
    return {
        "TYPE": type,
        "DATA": data
    }

def build_join_work(network_key, file_meta_data, node_meta_data):
    return {
        "TYPE": "SEND_REQUEST",
        "DATA": build_join_request(network_key, file_meta_data, node_meta_data)
    }

def build_file_request(ip, port, file_id, node_id):
    return {
        "IP": ip,
        "SERVER_PORT": port,
        "REQUEST": {
            "TYPE": "FETCH_FILE",
            "DATA": {"FILE": file_id, "NODE": node_id},
        },
    }

def build_serve_file_work(file_id, file_meta_data, file_buffer, node_id, ip, port, type_):
    return {
        "TYPE": "SERVE_FILE",
        "DATA": {
            "IP": ip,
            "SERVER_PORT": port,
            "META_DATA": {"FILE": file_id, "META_DATA": file_meta_data},
            "FILE_CONTENT": file_buffer,
            "NODE": node_id,
            "F_TYPE": type_
        },
    }

