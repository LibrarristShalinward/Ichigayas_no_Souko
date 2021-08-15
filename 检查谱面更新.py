from os.path import exists
import requests
import codecs
import json
import csv

source_path = "歌曲信息/歌曲难度.csv"

#基本函数
chart_path = lambda ID, diff = "expert": diff + "/" + str(ID).zfill(3) + ".json"

chart_exists = lambda ID, diff = "expert": exists(chart_path(ID, diff))

def get_chart(ID, diff = "expert"):
    url = "https://bestdori.com/api/charts/" + str(ID) + "/" + diff + ".json"
    client = requests.get(url)
    client.keep_alive = False
    return client.json()

def chart_download(ID, diff = "expert"):
    with codecs.open(chart_path(ID, diff), "w") as f:
        f.write(json.dumps(get_chart(ID, diff)))



#检查缺失谱面
download_list = []
with open(source_path, "r") as f:
    reader = csv.reader(f)
    for line in reader:
        diffs = ["easy", "naomal", "hard", "expert"]
        if len(line) == 8: diffs.append("special")
        missing = False
        ID = int(line[0])
        name = line[1]
        for diff in diffs:
            if not chart_exists(ID, diff):
                print("谱面缺失：\t曲目：%s\t难度：%s" %(name, diff))
                missing = True
                download_list.append((ID, diff))
        if not missing:
            print("%s谱面无缺失" %(name))
