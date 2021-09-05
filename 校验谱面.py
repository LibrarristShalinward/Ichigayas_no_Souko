import csv

from Ichigaya.chart import Chart

source_path = "歌曲信息（生成用）/歌曲难度.csv"

with open(source_path, "r", encoding = "UTF-8") as f:
    reader = csv.reader(f)
    for line in reader:
        diffs = ["easy", "normal", "hard", "expert"]
        if len(line) == 8: diffs.append("special")
        ID = int(line[0])
        name = line[1]
        for diff in diffs:
            checking_chart = Chart(ID, diff)
            checking_chart.to_path("谱面")
            status = True
            if checking_chart.exists():
                # size = getsize(chart_path(ID, diff))
                if checking_chart.size() < 2048: 
                    size = checking_chart.size()
                    print("谱面异常：\t大小：%i\t难度：%s\t曲目：%s" %(size, diff.ljust(8), name))
                    # remove(chart_path(ID, diff))
                    checking_chart.remove()

print("谱面校验完毕！")
