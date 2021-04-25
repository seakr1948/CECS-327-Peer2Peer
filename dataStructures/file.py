import datetime
import uuid
import json

from os import path
import fileSystemHelpers.checksum as checksum

class File:
    
    def __init__(self, relative_path: str, origin_node: uuid.UUID, encoder: list):

        self.relative_path = relative_path
        self.complete_path = path.abspath(self.relative_path)
        self.date_modified = checksum.get_time_stamp(self.complete_path)
        self.name = path.basename(self.complete_path)
        self.origin_node = origin_node
        self.check_sum = checksum.check_sum(self.relative_path, self.complete_path, encoder)
        
    def to_dict(self):
        
        meta_data = {
            "relative_path": self.relative_path,
            "data_modified": str(self.date_modified),
            "name": self.name,
            "origin_node": str(self.origin_node),
            "check_sum": self.check_sum
        }

        return meta_data