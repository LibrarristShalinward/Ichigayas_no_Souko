import codecs
import json
import warnings as w
from os import mkdir, remove
from os.path import exists, getsize
from .div import div_stateI, div_stateII

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

        self.min_retouch = None
        self.schedule = None
    
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
            self.__proccess_simo()
        return self.json
    
    def download(self, proccess = False):
        self.remove()
        self.load(proccess)
        self.save()
    
    def save(self):
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
    
    def get_min_retouch(self):
        if type(self.schedule) == type(None):
            self.__proccess_simo()
        
        min_retouch = (self.get_len(), 0., None), (self.get_len(), 0., None)

        beat_list = [(obj[2] if type(obj) == tuple else obj.beat) for obj in self.schedule]
        for i in range(len(beat_list) - 1):
            retouch = beat_list[i + 1] - beat_list[i]
            if retouch < min_retouch[0][0]:
                min_retouch = (retouch, beat_list[i], 
                    self.b_s_trans(beat_list[i + 1]) - self.b_s_trans(beat_list[i])), min_retouch[1]
        
        for hold in [hold for hold in self.keys["Hold"] if len(hold.slides) > 0]:
            node_list = [hold.touch] + [node for node in hold.slides if node.visible] + [hold.release]
            for i in range(len(node_list) - 1):
                retouch = node_list[i + 1].beat - node_list[i].beat
                if retouch < min_retouch[1][0]:
                    min_retouch = min_retouch[0], (retouch, node_list[i].beat, 
                        self.b_s_trans(node_list[i + 1].beat) - self.b_s_trans(node_list[i].beat))

        self.min_retouch = min_retouch
        return min_retouch
    
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
    
    def __proccess_simo(self, bar: int = 16):
        self.simo = []
        pre_pro_bars = (int(self.get_len()) // bar + 1) * [[]]
        for point in self.get_points():
            bar_idx = int(point[2] / float(bar))
            tar = pre_pro_bars[bar_idx]
            if tar == [] or point[2] > tar[-1][2]:
                pre_pro_bars[bar_idx] = tar + [point]
                continue
            for i in range(len(tar)):
                if point[2] < tar[i][2]:
                    pre_pro_bars[bar_idx] = pre_pro_bars[bar_idx][:i] + [point] + pre_pro_bars[bar_idx][i:]
                    break
                if point[2] == tar[i][2]:
                    self.simo.append(key.Simo(
                        tar[i], point, 
                        point[2], (tar[i][3], point[3])))
                    pre_pro_bars[bar_idx].pop(i)
                    break
        
        self.simo = sorted(self.simo, key = lambda simo: simo.beat)
        self.schedule = [] + self.simo
        for tar in pre_pro_bars:
            self.schedule += tar
        self.schedule = sorted(self.schedule, 
            key = lambda event: event[2] 
            if type(event) == tuple 
            else event.beat)
    
    # def set_hand(self):
    #     self.set_hand_simo()
    
    # def set_hand_simo(self):
    #     for simo in self.simo:
    #         simo.set_hand()

    def get_points(self):
        singles = self.keys["Single"] + self.keys["Flick"] + self.keys["Direct"]
        for point in singles:
            idx = self.keys["Single"].index(point) if type(point) == key.Single else self.keys["Flick"].index(point) if type(point) == key.Flick else self.keys["Direct"].index(point)
            yield type(point), None, point.beat, point.lane, idx
        for hold in self.keys["Hold"]:
            yield key.Hold, True, hold.touch.beat, hold.touch.lane, self.keys["Hold"].index(hold)
            yield key.Hold, False, hold.release.beat, hold.release.lane, self.keys["Hold"].index(hold)
    
    def get_point_list(self):
        return [point for point in self.get_points()]
    


    def div(self): 
        sI = div_stateI(self.keys, self.simo)
        for i in range(len(self.keys["Single"])): 
            self.keys["Single"][i].set_hand(sI["Single"][i])
        for i in range(len(self.keys["Flick"])): 
            self.keys["Flick"][i].set_hand(sI["Flick"][i])
        for i in range(len(self.keys["Direct"])): 
            self.keys["Direct"][i].set_hand(sI["Direct"][i])
        for i in range(len(self.keys["Hold"])): 
            self.keys["Hold"][i].set_hand(sI["Hold"][i])
        
        sII = div_stateII(self.keys)
        for rinfo in sII: 
            self.keys[rinfo[0]][rinfo[1]].set_hand(rinfo[2])



    def get_len(self):
        if self.len == 0:
            if self.json == None: self.load()
        return max(
            self.keys["Single"][-1].beat, 
            self.keys["Flick"][-1].beat if len(self.keys["Flick"]) > 0 else 0, 
            self.keys["Direct"][-1].beat if len(self.keys["Direct"]) > 0 else 0, 
            max([hold.release.beat 
            for hold in self.keys["Hold"]]) if len(self.keys["Hold"]) > 0 else 0)
    
    def __sec2beat(self, s):
        assert s >= 0, "请使用正秒数！"
        beat, bpm, time = self.stamp["beat"], self.stamp["bpm"], self.stamp["time"]
        if s >= time[-1]: 
            w.warn("超出乐曲长度！")
            return beat[-1] + (s - time[-1]) / 60. * bpm[-1]
        for tar in zip(beat, bpm, time):
            if tar[2] >= s:
                return tar[0] - (tar[2] - s) /60. * tar[1]
    
    def __beat2sec(self, b):
        assert b >= 0, "请使用正拍数！"
        beat, bpm, time = self.stamp["beat"], self.stamp["bpm"], self.stamp["time"]
        if b >= beat[-1]: 
            w.warn("超出乐曲长度！")
            return time[-1] + (b - beat[-1]) * 60. / bpm[-1]
        for tar in zip(beat, bpm, time):
            if tar[0] >= b:
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
