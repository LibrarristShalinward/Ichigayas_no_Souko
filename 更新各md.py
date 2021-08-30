import csv 
from Ichigaya.vision import MDChart

歌曲难度表source_file = "歌曲信息（生成用）/歌曲难度.csv"
歌曲难度表target_path = "歌曲信息（查询用）/歌曲难度表.md"
# md_text = [
#     "# 歌曲难度表\n", 
#     "<br>\n", 
#     "\n"
#     "----\n", 
#     "<br>\n", 
#     "<center>\n", 
#     "\n", 
#     "|ID|曲名|简写|Es|Nr|Hd|Ex|Sp|\n", 
#     "|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n"
# ]

歌曲难度表md = MDChart(
    歌曲难度表target_path, 
    "歌曲难度表", 
    ["ID", "曲名", "简写", "Es", "Nr", "Hd", "Ex", "Sp"])

歌曲难度表list = []

with open(歌曲难度表source_file, encoding = "UTF-8") as f:
    reader = csv.reader(f)
    歌曲难度表list = [line for line in reader]

# print(歌曲难度表list[0])

歌曲难度表md.write_table(歌曲难度表list)
歌曲难度表md.export()