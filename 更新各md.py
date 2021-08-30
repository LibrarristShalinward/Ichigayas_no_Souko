import csv
from Ichigaya import chart 
from Ichigaya.vision import MDChart
from Ichigaya.chart import get_charts
from Ichigaya.utils import id_name_trans



歌曲难度表source_file = "歌曲信息（生成用）/歌曲难度.csv"
all_charts = get_charts()



歌曲难度表md = MDChart(
    "歌曲信息（查询用）/歌曲难度表.md", 
    "歌曲难度表", 
    ["ID", "曲名", "简写", "Es", "Nr", "Hd", "Ex", "Sp"])
BPM排行md = MDChart(
    "歌曲信息（查询用）/速度排行.md", 
    "歌曲速度排行", 
    ["排位", "ID", "曲名", "BPM"])
按键数排行md = MDChart(
    "歌曲信息（查询用）/按键数排行.md", 
    "歌曲按键数排行", 
    ["排位", "ID", "曲名", "难度", "按键数"])
Combo排行md = MDChart(
    "歌曲信息（查询用）/连击排行.md", 
    "歌曲最大Combo数排行", 
    ["排位", "ID", "曲名", "难度", "最大Combo数"])



with open(歌曲难度表source_file, encoding = "UTF-8") as f:
    reader = csv.reader(f)
    歌曲难度表list = [line for line in reader]

charts = sorted(
    [chart for chart in all_charts if chart.get()[1] == "expert"], 
    key = lambda chart: chart.bpm, 
    reverse = True)
BPM排行list = [[
        charts.index(chart) + 1, 
        chart.get()[0], 
        id_name_trans(chart.get()[0]), 
        chart.bpm
    ] for chart in charts]
for i in range(1, len(BPM排行list)):
    if BPM排行list[i][-1] == BPM排行list[i - 1][-1]:
        BPM排行list[i][0] = BPM排行list[i - 1][0]

charts = sorted(
    all_charts, 
    key = lambda chart: chart.amount, 
    reverse = True)
按键数排行list = [[
        charts.index(chart) + 1, 
        chart.get()[0], 
        id_name_trans(chart.get()[0]), 
        chart.get()[1], 
        chart.amount
    ] for chart in charts]
for i in range(1, len(按键数排行list)):
    if 按键数排行list[i][-1] == 按键数排行list[i - 1][-1]:
        按键数排行list[i][0] = 按键数排行list[i - 1][0]

charts = sorted(
    charts, 
    key = lambda chart: chart.max_combo, 
    reverse = True)
Combo排行list = [[
        charts.index(chart) + 1, 
        chart.get()[0], 
        id_name_trans(chart.get()[0]), 
        chart.get()[1], 
        chart.max_combo
    ] for chart in charts]
for i in range(1, len(Combo排行list)):
    if Combo排行list[i][-1] == Combo排行list[i - 1][-1]:
        Combo排行list[i][0] = Combo排行list[i - 1][0]



歌曲难度表md.write_table(歌曲难度表list)
BPM排行md.write_table(BPM排行list)
按键数排行md.write_table(按键数排行list)
Combo排行md.write_table(Combo排行list)

歌曲难度表md.export()
BPM排行md.export()
按键数排行md.export()
Combo排行md.export()