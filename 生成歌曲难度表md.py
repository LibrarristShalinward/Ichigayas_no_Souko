import csv 

source_file = "歌曲信息（生成用）/歌曲难度.csv"
target_path = "歌曲信息（查询用）/歌曲难度表.md"
md_text = [
    "# 歌曲难度表\n", 
    "<br>\n", 
    "\n"
    "----\n", 
    "<br>\n", 
    "<center>\n", 
    "\n", 
    "|ID|曲名|简写|Es|Nr|Hd|Ex|Sp|\n", 
    "|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n"
]

with open(source_file, encoding = "UTF-8") as f:
    reader = csv.reader(f)
    for line in reader:
        md_line = "|"
        for item in line:
            md_line += item + "|"
        md_text.append(md_line + '\n')

with open(target_path, "w", encoding = "UTF-8") as f:
    f.writelines(md_text)
