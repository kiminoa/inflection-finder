import json

class JSONDOA:
    """
    JSON Data Access Object (DOA)
    """
    
    def __init__(self, filename):
        self.filename = filename
        self.dict = {}
        
    def store(self):
        """
        store self.dict as JSON data; overwrites existing file if retrieve
        was not called before appending.
        """
        with open(self.filename, "w") as json_file:
            json.dump(self.dict, json_file, ensure_ascii=False, encoding='utf-8')
                
    def retrieve(self):
        """
        retrieve JSON data into self.dict
        """
        with open(self.filename) as json_file:
            self.dict = json.load(json_file)
        return self.dict
        
    def append(self, data):
        """
        append new data to dictionary; used to mimic a streamable data object since
        JSON isn't
        """
        self.dict.update(data)