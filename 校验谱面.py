from os.path import exists, getsize
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

with open(source_path, "r", encoding = "UTF-8") as f:
    reader = csv.reader(f)
    for line in reader:
        diffs = ["easy", "normal", "hard", "expert"]
        if len(line) == 8: diffs.append("special")
        ID = int(line[0])
        name = line[1]
        for diff in diffs:
            status = True
            if chart_exists(ID, diff):
                size = getsize(chart_path(ID, diff))
                if size < 2048: 
                    print("谱面异常：\t大小：%i\t难度：%s\t曲目：%s" %(size, diff.ljust(8), name))
                    remove(chart_path(ID, diff))

print("谱面校验完毕！")