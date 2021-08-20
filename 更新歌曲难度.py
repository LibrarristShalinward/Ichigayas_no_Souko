import csv

name_path = "歌曲信息/歌曲列表.csv"
abbr_path = "歌曲信息/歌曲名简写.csv"
target_path = "歌曲信息/歌曲难度.csv"

#拼接歌曲名列表与简称列表
song_name = []
with open(name_path, "r", encoding = "UTF-8") as name_file:
    with open(abbr_path, "r") as abbr_file:
        reader = zip(csv.reader(name_file), csv.reader(abbr_file))
        for name, abbr in reader:
            if abbr == []:
                song_name.append(name + [""])
            else:
                song_name.append(name + abbr)



#获取歌曲难度JSON
import requests
clinet = requests.get("https://bestdori.com/api/songs/all.5.json")
clinet.keep_alive = False
result = clinet.json()



#整理输出列表
song_info = []
for i in song_name:
    diff = result[i[0]]["difficulty"]
    info_seq = i + [diff["0"]["playLevel"], diff["1"]["playLevel"], diff["2"]["playLevel"], diff["3"]["playLevel"]]
    if len(diff) == 5:
        info_seq.append(diff["4"]["playLevel"])
    song_info.append(info_seq)



#输出csv
with open(target_path, "w", encoding = "UTF-8", newline = "") as target_file:
    writer = csv.writer(target_file)
    writer.writerows(song_info)