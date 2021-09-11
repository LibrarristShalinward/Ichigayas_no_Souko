import csv
import 初始化路径
from Ichigaya.chart import Chart

main_path = "././"
source_path = main_path + "歌曲信息（生成用）/歌曲难度.csv"
target_path = main_path + "谱面"

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
            new_chart = Chart(ID, diff)
            new_chart.set_name(name)
            new_chart.to_path(target_path)
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
        missing_chart.remove()
        print("谱面下载失败：" + str(info[0]) + "." + info[2] + "-" + info[1])

print("谱面检查完毕!")
