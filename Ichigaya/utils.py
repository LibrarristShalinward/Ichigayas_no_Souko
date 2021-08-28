import csv


id_name_trans = lambda obj: id2name(obj) if isinstance(obj, int) else name2id(obj)

歌曲列表路径 = "歌曲信息/歌曲列表.csv"
with open(歌曲列表路径, "r", encoding = "utf-8") as f:
    reader = csv.reader(f)
    歌曲列表 = [[int(line[0]), line[1]] for line in reader]
id_list = [歌曲[0] for 歌曲 in 歌曲列表]
name_list = [歌曲[1] for 歌曲 in 歌曲列表]

def name2id(name: str):
    assert name in name_list, "找不到歌曲名"
    return id_list[name_list.index(name)]

def id2name(id: int):
    assert id in id_list, "找不到歌曲id"
    return name_list[id_list.index(id)]
