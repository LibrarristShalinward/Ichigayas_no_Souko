import 初始化路径
from Ichigaya.vision.html_chart import ChartView
from Ichigaya.chart import Chart
from Ichigaya.vision import StaticHTMLChart, DynamicHTMLChart
from Ichigaya import id_name_trans
import argparse

main_path = "././"
target_path = main_path + "谱面"
parser = argparse.ArgumentParser("市ヶ谷家离线谱面模拟器交互终端")

parser.add_argument("-I", "--ID")
parser.add_argument("-d", "--diff", default = "expert")
parser.add_argument("-c", "--curve", default = "linear")
parser.add_argument("-f", "--falling_speed", default = None)
parser.add_argument("-m", "--mode", default = "dynamic")
parser.add_argument("-s", "--step", default = 2)
parser.add_argument("-r", "--refresh_frequency", default = 60)
parser.add_argument("-l", "--screen_range", default = 64)
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
