import requests
from os.path import exists
from os import remove
import codecs
import json



init_chart_path = lambda ID, diff = "expert": diff + "/" + str(ID).zfill(3) + ".json"



class chart:
    def __init__(self, ID, diff = "expert") -> None:
        self.ID = ID
        self.diff = diff
        self.path = init_chart_path(ID, diff)
        self.exists = lambda self: exists(self.path)
        self.url = "https://bestdori.com/api/charts/" + str(ID) + "/" + diff + ".json"
    
    def load(self): 
        if self.exists():
            with codecs.open(self.path, "r") as f:
                self.json = json.load(f)
        else:
            client = requests.get(self.url)
            client.keep_alive = False
            if client.status_code == 200:
                self.json = client.json()
            else: self.json = None
        return self.json
    
    def download(self):
        self.remove()
        self.load()
        with codecs.open(self.path, "w") as f:
            f.write(json.dumps(self.json))
    
    def remove(self):
        if self.exists(): remove(self.path)
    
    def to_path(self, path):
        self.path = path + "/" + init_chart_path(self.ID, self.diff)
    
    def set_path(self, path):
        self.path = path