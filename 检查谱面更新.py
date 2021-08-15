from os.path import exists
from os import remove
import requests
import codecs
import json
import csv

source_path = "歌曲信息/歌曲难度.csv"

#基本函数
chart_path = lambda ID, diff = "expert": "谱面/" + diff + "/" + str(ID).zfill(3) + ".json"

chart_exists = lambda ID, diff = "expert": exists(chart_path(ID, diff))

def get_chart(ID, diff = "expert"):
    url = "https://bestdori.com/api/charts/" + str(ID) + "/" + diff + ".json"
    client = requests.get(url)
    client.keep_alive = False
    return client.json()

def chart_download(ID, diff = "expert"):
    with codecs.open(chart_path(ID, diff), "w") as f:
        f.write(json.dumps(get_chart(ID, diff)))

def chart_remove(ID, diff = "expert"):
    if chart_exists(): remove(chart_path(ID, diff))

#检查缺失谱面
download_list = []
with open(source_path, "r", encoding = "UTF-8") as f:
    reader = csv.reader(f)
    for line in reader:
        diffs = ["easy", "normal", "hard", "expert"]
        if len(line) == 8: diffs.append("special")
        missing = False
        ID = int(line[0])
        name = line[1]
        for diff in diffs:
            if not chart_exists(ID, diff):
                print("谱面缺失：\t难度：%s\t曲目：%s" %(diff.ljust(8), name))
                missing = True
                download_list.append((ID, diff, name))
        if not missing:
            print("%s谱面无缺失" %(name))



#下载缺失谱面
for ID, diff, name in download_list:
    try:
        chart_download(ID, diff)
        print("谱面下载成功：" + str(ID) + "." + name + "-" + diff)
    except:
        chart_remove(ID, diff)
        print("谱面下载失败：" + str(ID) + "." + name + "-" + diff)
