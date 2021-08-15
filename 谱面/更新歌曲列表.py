import csv
import requests

target_path = "谱面/歌曲列表.csv"

#获取歌曲列表
clinet = requests.get("https://bestdori.com/api/songs/all.1.json")
clinet.keep_alive = False
result = clinet.json()



#整理歌曲列表
write_list = []
for i, j in zip(result.keys(), result.values()):
    write_list.append([i, j['musicTitle'][0]])



#输出列表为csv
with open(target_path, "w", newline = "", encoding = "UTF-8") as f:
    writer = csv.writer(f)
    writer.writerows(write_list)
