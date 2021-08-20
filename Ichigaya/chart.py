import requests
from os.path import exists
from os import error, remove
import codecs
import json



init_chart_path = lambda ID, diff = "expert": diff + "/" + str(ID).zfill(3) + ".json"
diffs = ["easy", "normal", "hard", "expert", "special"]



class chart:
    def __init__(self, ID = None, diff = "expert") -> None:
        self.__ID = ID
        self.__diff = diff
        self.__name = ""
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
    
    def set_ID(self, ID = None):
        self.__ID = ID
    
    def set_diff(self, diff = "expert"):
        if diff in diffs:
            self.__diff = diff
        else:
            raise TypeError("Unrecognized difficulty Type \"" + diff + "\"")
    
    def set_name(self, name = ""):
        self.__name = name
    
    def get(self): 
        return self.__ID, self.__diff, self.__name
    
    def set(self, ID = None, diff = "expert", name = ""):
        self.set_ID(ID)
        self.set_diff(diff)
        self.set_name(name)