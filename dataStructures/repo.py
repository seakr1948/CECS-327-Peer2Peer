from io import BytesIO
import os
import os.path as path
import json
import uuid

from dataStructures.file import File
from os import walk

class Repo:
    def __init__(self,
        shared_folder_relative_path: str, uuid: uuid.UUID, watcher):

        # Standard node data
        self.folder_relative_path = shared_folder_relative_path
        self.folder_complete_path = path.abspath(self.folder_relative_path)
        self.meta_data_path = path.join(self.folder_complete_path, "meta.json")
        
        self.encoder = [9, 4, 3, 6]
        self.ignore_file_names = []
        self.uuid = uuid
        self.watcher = watcher

    def add_ignore_files(self, file_names: list):
        file_names = [name.strip("\n") for name in file_names]
        self.ignore_file_names.extend(file_names)

    def load_ignore_file_names(self):
        try:
            path_ = path.join(self.folder_complete_path, ".ignore")
            with open(path_) as file_names:
                self.add_ignore_files(file_names.readlines())
        except:
            print("No ignored files")

        print(self.ignore_file_names)

    def init_meta_file(self):
        file_structure = []

        # Walk the tree of the directory and append a zipped stucture of directory and file names
        for (dirpath, dirnames, filenames) in walk(self.folder_complete_path):
            file_structure.append((dirpath, filenames))

        file_objects = []
        # Loop through each directory
        for folder in file_structure:
            folder_files = folder[1]  # Files in directory
            complete_folder_path = folder[0]  # Path of the directory

            # Loop through each file name in directory
            for file in folder_files:
                # If not part of the ignore files
                if file not in self.ignore_file_names:
                    # Compute the relative path of the file
                    paths = [
                        path.relpath(
                            complete_folder_path, self.folder_relative_path
                        ),
                        file,
                    ]
                    relative_path_of_file = path.join(*paths)

                    # Make a File object out of it, see: dataStuctures.file
                    file_objects.append(
                        File(
                            self.folder_complete_path,
                            relative_path_of_file,
                            self.uuid,
                            self.encoder,
                        )
                    )

        # Get all meta_data from each file in a list
        meta_data = {}
        for file in file_objects:
            meta_data.update(file.to_dict())

        self.write_to_meta_data_file(meta_data)

    def write_to_meta_data_file(self, data):
        # Open meta data
        meta_data_file = open(self.meta_data_path, "w")

        # Make a jsonstring out of the data and write to the file
        json.dump(
            data,
            meta_data_file,
            indent=4,
            separators=(", ", ": "),
            sort_keys=True,
        )

        # Close file
        meta_data_file.close()

    def load_meta_data(self):

        try:
            path_to_meta = path.join(self.folder_complete_path, "meta.json")
            file = open(path_to_meta, "r")

            self.meta_data = json.loads(file.read())
        except:
            print("meta does not exist")

    def update_file_meta_data(self, file_uuid, meta_data):
        self.load_meta_data()
        self.meta_data.update({file_uuid: meta_data})
        self.write_to_meta_data_file(self.meta_data)

    def fetch_file_data(self, uuid_str):
        self.load_meta_data() 
        return self.meta_data[uuid_str]

    def fetch_file(self, uuid_str):
        file_meta_data = self.fetch_file_data(uuid_str)

        relative_file_path = file_meta_data["relative_path"]
        complete_file_path = path.join(
            self.folder_complete_path, relative_file_path
        )

        file_bytes = open(complete_file_path, "rb")

        copy_of_file = BytesIO(file_bytes.read())

        file_bytes.close()

        return copy_of_file

    def add_file(self, file_uuid, meta_data, file_content):
        self.update_file_meta_data(file_uuid, meta_data)
        self.write_file_content(meta_data["relative_path"], file_content)

    def write_file_content(self, relative_path, file_content: BytesIO):
        file = open(path.join(self.folder_complete_path, relative_path), "wb")
        file.write(file_content.read())
        file.close()

    def update_file_meta(self, file_uuid, updated_meta: dict):
        self.load_meta_data()
        file_meta_data = self.meta_data[file_uuid]

        for key in updated_meta.keys():
            file_meta_data.update({key: updated_meta[key]})
    
    def get_files(self):
        self.load_meta_data()
        list_keys = self.meta_data.keys()
        list_to = []
        for key in list_keys:
            list_to.append(str(key))
        return list_to

    def delete(self, uuid):
        self.load_meta_data()
        path_ = os.path.join(self.folder_complete_path, self.meta_data[uuid]["relative_path"])
        os.remove(os.path.abspath(path_))
        self.meta_data.pop(uuid)
        self.write_to_meta_data_file(self.meta_data)
