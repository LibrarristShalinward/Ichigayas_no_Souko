import 初始化路径
from Ichigaya.vision.html_chart import ChartView
from Ichigaya.chart import Chart
from Ichigaya.vision import StaticHTMLChart, DynamicHTMLChart
from Ichigaya import id_name_trans
import argparse

main_path = "././"
target_path = main_path + "谱面"
parser = argparse.ArgumentParser("市ヶ谷家离线谱面模拟器交互终端")

parser.add_argument("-I", "--ID", 
    help = "歌曲编号或名称")
parser.add_argument("-d", "--diff", default = "expert", 
    help = "谱面难度，默认为Ex；输入格式为格式名小写全词，即easy/normal/hard/expert/special")
parser.add_argument("-c", "--curve", default = "linear", 
    help = "新版本绿条生成插值方式，默认为线性插值-linear；另可设为三次样条插值-cubic")
parser.add_argument("-f", "--falling_speed", default = None, 
    help = "谱面纵向延伸率，默认为2；可选值为1/2/4，单位为(*64行/秒)")
parser.add_argument("-m", "--mode", default = "dynamic", 
    help = "生成像素谱面模式，默认为动态谱面-d/dynamic；另有静态模式-s/static可选")
parser.add_argument("-s", "--step", default = 2, 
    help = "时间分辨率/每次刷新行数（仅支持动态谱面），默认为2；可选值为2/4/8")
parser.add_argument("-r", "--refresh_frequency", default = 60, 
    help = "刷新率（仅支持动态谱面），默认为60；可选值为10/30/60")
parser.add_argument("-l", "--screen_range", default = 64, 
    help = "屏幕显示行数（仅支持动态谱面），默认为64；可选值为16/32/64")
parser.add_argument("-j", "--use_java", default = True)
args = parser.parse_args()

id, curve_method, bps, mode, lps, rf, sr, js = args.ID, args.curve.lower(), args.falling_speed, args.mode.lower(), args.step, args.refresh_frequency, args.screen_range, args.use_java

if type(id) == str:
    id = id_name_trans(id)
else:
    assert type(id) == int
assert curve_method in ["linear", "cubic"]
if bps:
    assert bps in [1, 2, 4]
assert mode in ["s", "static", "d", "dynamic"]
if lps:
    assert lps in [2, 4, 8]
if rf:
    assert rf in [10, 30, 60]
if sr:
    assert sr in [16, 32, 64]
assert js in [True, False, None]


origin_chart = Chart(id, args.diff)
origin_chart.to_path(target_path)
_ = origin_chart.load()
origin_chart.div()
view = ChartView(origin_chart, bps = bps, curve_method = curve_method)

if mode[0] == "s":
    html = StaticHTMLChart(view)
else:
    html = DynamicHTMLChart(view, lps = lps, rf = rf, sr = sr, js = js)

if mode[0] == "d" and not js:
    html.run()
else:
    html.export()
    html.view()
