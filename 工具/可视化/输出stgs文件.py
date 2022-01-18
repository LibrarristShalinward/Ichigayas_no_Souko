import 初始化路径
from Ichigaya.vision import to_stgs
from Ichigaya.chart import Chart
import argparse
from Ichigaya import id_name_trans

main_path = "././"
target_path = main_path + "谱面"
parser = argparse.ArgumentParser("BanGDream Stage Simulator谱面文件导出")

parser.add_argument("ID", help = "歌曲编号或名称")
parser.add_argument("-d", "--diff", default = "expert", 
    help = "谱面难度，默认为Ex；输入格式为格式名小写全词，即easy/normal/hard/expert/special")
parser.add_argument("-p", "--path", default = None, 
    help = "导出地址与文件名，默认地址为主文件夹，文件名为[id]-[曲名]-[难度].stgs")
args = parser.parse_args()

id = args.ID
try: 
    id = int(id)
except: 
    id = id_name_trans(id)

chart = Chart(id, args.diff)
chart.load()
to_stgs(chart, args.path)