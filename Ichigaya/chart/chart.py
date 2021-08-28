import codecs
import json
import warnings as w
from os import mkdir, remove
from os.path import exists, getsize

import requests

from . import key

init_chart_path = lambda ID, diff = "expert": diff + "/" + str(ID).zfill(3) + ".json"
diffs = ["easy", "normal", "hard", "expert", "special"]



class Chart:
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
            "bpm": [], 
            "time": []
        }
        self.const_speed = None
    
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
        
        self.amount = sum([len(obj_list) for obj_list in self.keys.values()])
        combo_hold = sum(len(hold.slides) + 2 for hold in self.keys["Hold"])
        if self.__diff == "special":
            combo_hold = sum(
                sum(
                    1 for slide in hold.slides if slide.visible
                ) + 2 for hold in self.keys["Hold"])
        self.max_combo = self.amount - len(self.keys["Hold"]) + combo_hold
    
    def __proccess_time(self):
        end_beat = self.get_len()
        for idx in self.stamp.keys():
            self.stamp[idx] = []
        for obj in self.json:
            if obj["type"] == "BPM":
                self.stamp["beat"].append(obj["beat"])
                self.stamp["bpm"].append(obj["bpm"])
        self.stamp["beat"].pop(0)
        self.const_speed = len(self.stamp["beat"]) == 0
        self.stamp["beat"].append(end_beat)
        self.stamp["time"].append(60. / self.stamp["bpm"][0] * self.stamp["beat"][0])
        self.bpm, last_beats = self.stamp["bpm"][0], self.stamp["beat"][0]
        if not self.const_speed:
            for i in range(1, len(self.stamp["beat"])):
                self.stamp["time"].append(
                    self.stamp["time"][-1] + 60. / self.stamp["bpm"][i] * (
                        self.stamp["beat"][i] - self.stamp["beat"][i-1]))
                if self.stamp["beat"][i] - self.stamp["beat"][i-1] > last_beats:
                    self.bpm, last_beats = self.stamp["bpm"][i], self.stamp["beat"][i] - self.stamp["beat"][i-1]
        self.b_s_trans = lambda point, is_beat = True: self.__beat2sec(point) if is_beat else self.__sec2beat(point)
    
    def get_len(self):
        if self.len == 0:
            if self.json == None: self.load()
            return self.json[-1]["beat"] if "beat" in self.json[-1].keys() else self.json[-1]["connections"][-1]["beat"]
    
    def __sec2beat(self, s):
        assert s >= 0, "请使用正秒数！"
        beat, bpm, time = self.stamp["beat"], self.stamp["bpm"], self.stamp["time"]
        if s > time[-1]: 
            w.warn("超出乐曲长度！")
            return beat[-1] + (s - time[-1]) / 60. * bpm[-1]
        for tar in zip(beat, bpm, time):
            if tar[2] > s:
                return tar[0] - (tar[2] - s) /60. * tar[1]
    
    def __beat2sec(self, b):
        assert b >= 0, "请使用正拍数！"
        beat, bpm, time = self.stamp["beat"], self.stamp["bpm"], self.stamp["time"]
        if b > beat[-1]: 
            w.warn("超出乐曲长度！")
            return time[-1] + (b - beat[-1]) * 60. / bpm[-1]
        for tar in zip(beat, bpm, time):
            if tar[0] > b:
                return tar[2] - (tar[0] - b) *60. / tar[1]
        
def get_charts(diff = None, path = "谱面", process = True):
    if diff == None:
        return get_charts(diffs, path, process)
    if isinstance(diff, list):
        chart_list = []
        for single in diff: 
            chart_list += get_charts(single, path, process)
        return chart_list
    assert isinstance(diff, str), "难度须为str变量"
    assert diff in diffs, "难度" + diff + "无法识别"
    max_id = 500
    chart_list = [Chart(id, diff) for id in range(1, max_id)]
    for chart in chart_list: chart.to_path(path)
    chart_list = [chart for chart in chart_list if chart.exists()]
    for chart in chart_list: chart.load(process)
    return sorted(
        chart_list, 
        key = lambda chart: chart.get()[0] * 10 + diffs.index(chart.get()[1]))
