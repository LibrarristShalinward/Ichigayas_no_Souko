# from os.path import exists
# from os import remove
# import requests
# import codecs
# import json
import csv
from Ichigaya import chart

source_path = "歌曲信息/歌曲难度.csv"

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
            new_chart = chart.chart(ID, diff)
            new_chart.set_name(name)
            new_chart.to_path("谱面")
            if not new_chart.exists():
                print("谱面缺失：\t难度：%s\t曲目：%s" %(diff.ljust(8), name))
                missing = True
                download_list.append(new_chart)
        if not missing:
            print("%s谱面无缺失" %(name))



#下载缺失谱面
for missing_chart in download_list:
    info = missing_chart.get()
    try:
        missing_chart.download()
        print("谱面下载成功：" + str(info[0]) + "." + info[2] + "-" + info[1])
    except Exception:
        missing_chart.remobe()
        print("谱面下载失败：" + str(info[0]) + "." + info[2] + "-" + info[1])

print("谱面检查完毕!")