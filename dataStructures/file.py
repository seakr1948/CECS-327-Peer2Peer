import datetime
import uuid
import json

from os import path
import fileSystemHelpers.checksum as checksum


class File:
    def __init__(
        self,
        folder_complete_path: str,
        relative_path: str,
        origin_node: uuid.UUID,
        encoder: list,
        file_uuid=None,
    ):
        if file_uuid == None:
            self.file_uuid = uuid.uuid4()
        else:
            self.file_uuid = file_uuid

        self.relative_path = relative_path
        self.complete_path = path.join(folder_complete_path, relative_path)
        self.date_modified = checksum.get_time_stamp(self.complete_path)
        self.name = path.basename(self.complete_path)
        self.origin_node = origin_node
        self.check_sum = checksum.check_sum(
            self.relative_path, self.complete_path, encoder
        )
        self.file_size_bytes = checksum.get_file_size(self.complete_path)

    def to_dict(self):

        meta_data = {
            str(self.file_uuid): {
                "relative_path": self.relative_path,
                "data_modified": str(self.date_modified),
                "name": self.name,
                "origin_node": str(self.origin_node),
                "check_sum": self.check_sum,
                "file_size": self.file_size_bytes
            }
        }

        return meta_data
