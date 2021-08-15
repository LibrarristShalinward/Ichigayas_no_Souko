from os.path import exists
from os import remove
import csv
import json
import codecs



source_path = "歌曲信息/歌曲难度.csv"

#基本函数
chart_path = lambda ID, diff = "expert": "谱面/" + diff + "/" + str(ID).zfill(3) + ".json"

chart_exists = lambda ID, diff = "expert": exists(chart_path(ID, diff))

def chart_remove(ID, diff = "expert"):
    if chart_exists(ID, diff): remove(chart_path(ID, diff))

def chart_load(ID, diff = "expert"):
    if not chart_exists(ID, diff): return None
    with codecs.open(chart_path(ID, diff), "r", encoding = "UTF-8") as f:
        return json.load(f)

with codecs.open(source_path, "r", encoding = "UTF-8") as f:
    reader = csv.reader(f)
    for line in reader:
        diffs = ["easy", "normal", "hard", "expert"]
        if len(line) == 8: diffs.append("special")
        ID = int(line[0])
        name = line[1]
        for diff in diffs:
            if chart_exists(ID, diff):
                chart = chart_load(ID, diff)
                if len(chart) <= 25:
                    print("谱面异常：\t难度：%s\t曲目：%s" %(diff.ljust(8), name))
                else: 
                    print("谱面正常：\t难度：%s\t曲目：%s" %(diff.ljust(8), name))