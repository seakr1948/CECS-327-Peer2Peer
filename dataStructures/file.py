import datetime
import uuid
import json

class file_:
    
    def __init__(self,
        relative_path: str, date_modified: datetime.datetime, 
        name: str, origin_node: uuid.UUID, check_sum: int
        ):

        self.relative_path = relative_path
        self.date_modified = date_modified
        self.name = name
        self.origin_node = origin_node
        self.check_sum = check_sum
        
    def to_json(self):
        
        meta_data = {
            "relative_path": self.relative_path,
            "data_modified": self.date_modified
            "name": self.name,
            "origin_node": self.origin_node
            "check_sum": self.check_sum
        }

        return json.dumps(meta_data)