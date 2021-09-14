import csv
import 初始化路径
from Ichigaya.chart import Chart

main_path = "././"
source_path = main_path + "歌曲信息（生成用）/歌曲难度.csv"
target_path = main_path + "谱面"

with open(source_path, "r", encoding = "UTF-8") as f:
    reader = csv.reader(f)
    for line in reader:
        diffs = ["easy", "normal", "hard", "expert"]
        if len(line) == 8: diffs.append("special")
        ID = int(line[0])
        name = line[1]
        for diff in diffs:
            checking_chart = Chart(ID, diff)
            checking_chart.to_path(target_path)
            status = True
            if checking_chart.exists():
                if checking_chart.size() < 2048: 
                    size = checking_chart.size()
                    print("谱面异常：\t大小：%i\t难度：%s\t曲目：%s" %(size, diff.ljust(8), name))
                    checking_chart.remove()

print("谱面校验完毕！")
