import codecs
import json
from os import mkdir, remove
from os.path import exists, getsize

import requests

from . import key

init_chart_path = lambda ID, diff = "expert": diff + "/" + str(ID).zfill(3) + ".json"
diffs = ["easy", "normal", "hard", "expert", "special"]



class chart:
    def __init__(self, ID = None, diff = "expert") -> None:
        self.__ID = ID
        self.__diff = diff
        self.__name = ""
        self.file = init_chart_path(ID, diff)
        self.path = diff
        self.url = "https://bestdori.com/api/charts/" + str(ID) + "/" + diff + ".json"
        self.json = None
        
        self.keys = {}
        self.len = 0
        self.stamp = {
            "beat": [], 
            "bpm": []
        }
    
    def exists(self):return exists(self.file)

    def load(self, process = True): 
        if self.exists():
            with codecs.open(self.file, "r") as f:
                self.json = json.load(f)
        else:
            client = requests.get(self.url)
            client.keep_alive = False
            if client.status_code == 200:
                self.json = client.json()
            else: self.json = None
        if process and self.json != None:
            self.__proccess_keys()
            self.__proccess_time()
        return self.json
    
    def download(self, proccess = False):
        self.remove()
        self.load(proccess)
        if not exists(self.path): mkdir(self.path)
        with codecs.open(self.file, "w") as f:
            f.write(json.dumps(self.json))
    
    def remove(self):
        if self.exists(): remove(self.file)
    
    def to_path(self, path):
        self.file = path + "/" + init_chart_path(self.__ID, self.__diff)
        self.path = path + "/" + self.__diff
    
    def set_path(self, path):
        self.file = path
    
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
    
    def size(self):
        if self.exists():
            return getsize(self.file)
        else: return 0
    
    def set(self, ID = None, diff = "expert", name = ""):
        self.set_ID(ID)
        self.set_diff(diff)
        self.set_name(name)
    


    def __proccess_keys(self):
        if self.json == None: self.load()
        self.keys = {
            "Single": [], 
            "Hold": [], 
            "Flick": [], 
            "Direct": []}
        for obj in self.json:
            if obj["type"] == "Single":
                if "flick" in obj.keys() and obj["flick"]:
                    self.keys["Flick"].append(key.Flick(obj))
                else:
                    self.keys["Single"].append(key.Single(obj))
            if obj["type"] == "Directional":
                self.keys["Direct"].append(key.Direct(obj))
            if obj["type"] in ["Long", "Slide"]:
                self.keys["Hold"].append(key.Hold(obj))
    
    def __proccess_time(self):
        end_beat = self.get_len()
        for obj in self.json:
            if obj["type"] == "BPM":
                self.stamp["beat"].append(obj["beat"])
                self.stamp["bpm"].append(obj["bpm"])
        self.stamp["beat"].pop(0)
        self.stamp["beat"].append(end_beat)
    
    def get_len(self):
        if self.len == 0:
            if self.json == None: self.load()
            return self.json[-1]["beat"]
