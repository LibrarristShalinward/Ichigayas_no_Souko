from scipy.interpolate.interpolate import interp1d
from Ichigaya.chart import key
from ..chart import Single, Flick, Hold, Direct, Simo, Chart, slide
import json
import codecs
from os.path import dirname
from scipy.interpolate import interp1d
from numpy import array
import logging
import datetime

get_now_time = lambda: datetime.datetime.strftime(datetime.datetime.now(), "%X")
current_path = dirname(__file__)
std_lane_width = 15
l2i = lambda lane: int(1. + (std_lane_width + 1.) * lane)
lane_range = lambda lane: (l2i(lane), l2i(lane) + std_lane_width)

class ViewSkin():
    key_names = ["size"], ["Single", "Flick", "Hold_touch", "Hold_release", "Hold_flick", "Hold_body", "Hold_node", "Left_1", "Right_1"], ["Left_2", "Right_2"], ["Left_3", "Right_3"], ["Simo_link"]
    def __init__(self, type = "classic") -> None:
        self.type = type
        self.path = current_path + "\\html_chart_skin\\" + self.type + ".json"
        self.load()
        self.verify()
    
    def load(self):
        with codecs.open(self.path, "r") as f:
            self.json = json.load(f)
    
    def verify(self):
        for group in self.key_names:
            for obj in group:
                assert obj in self.json.keys(), "键名缺失：" + obj
        
        act_lane_width = self.json[self.key_names[0][0]]
        assert act_lane_width == std_lane_width, "键宽异常：应为%i，实际为%i"%(std_lane_width, act_lane_width)

        for i, group in enumerate(self.key_names[1:4]):
            std_len = std_lane_width * (i + 1) + i
            for obj in group:
                act_len = len(self.json[obj])
                assert act_len == std_len, "皮肤长度异常：键%s长度应为%i，实际为%i"%(obj, std_len, act_len)
        obj = self.key_names[4][0]
        std_len, act_len = 1, len(self.json[obj])
        assert act_len == std_len, "皮肤长度异常：键%s长度应为%i，实际为%i"%(obj, std_len, act_len)
    
    def __call__(self):
        return self.json

default_skin = ViewSkin("classic")

class LayerView():
    def __init__(self):
        self.ocp_lines = []

    def view_layer(self):
        def layer(_):
            return None
        return layer

class LayerGroupView(LayerView):
    def __init__(self, group: list = [],cache = True):
        for layer_view in group:
            assert isinstance(layer_view, LayerView)
        super().__init__()
        self.layer_group = group
        self.view_cache = []

        for layer_view in group:
            self.ocp_lines += layer_view.ocp_lines
        self.ocp_lines = list(set(self.ocp_lines))
        self.ocp_lines = sorted(self.ocp_lines)
        
        if cache: self.process_cache()
    
    def process_cache(self, skin: ViewSkin = default_skin):
        if self.view_cache == []:
            layer = self.view_layer(skin)
            for l in self.ocp_lines:
                line_cache = ""
                for p in range((std_lane_width + 1) * 7 + 1):
                    super_char = layer((l, p))
                    line_cache += "#" if type(super_char) == type(None) else super_char
                self.view_cache.append(line_cache)
    
    def view_layer(self, skin: ViewSkin = default_skin):
        if len(self.view_cache) > 0:
            def cache_layer(idx):
                l, p = idx
                if l in self.ocp_lines:
                    i = self.ocp_lines.index(l)
                    return self.view_cache[i][p]
            return cache_layer
        def layer(idx):
            l, _ = idx
            view = None
            for layer_view in self.layer_group:
                if l in layer_view.ocp_lines:
                    view = layer_view.view_layer(skin)(idx)
                    if type(view) != type(None) and view != "#":
                        break
            return view
        return layer

class ClearChartView(LayerView):
    def __init__(self, length):
        self.ocp_lines = [i for i in range(length)]

    def view_layer(self, _: ViewSkin = default_skin):
        def layer(idx):
            _, p = idx
            if p % (std_lane_width + 1) == 0:
                return "|"[0]
            return None
        return layer

class SingleView(Single, LayerView):
    def __init__(self, single, b2l, hold_rls = None) -> None:
        Single.__init__(self, beat = single.beat, lane = single.lane)
        self.line = int(b2l(single.beat))
        self.hand = getattr(single, "hand", None)
        self.ocp_lines = [self.line]
        if type(hold_rls) == type(None):
            if type(single) == Flick:
                self.view_idx = "Flick"
            elif type(single) == Single:
                self.view_idx = "Single"
            else:
                self.view_idx = "Hold_node"
        else:
            assert type(single) != slide
            if hold_rls:
                self.view_idx = "Hold_flick" if type(single) == Flick else "Hold_release"
            else: 
                assert type(single) == Single
                self.view_idx = "Hold_touch"
    
    def get_view(self, skin: ViewSkin = default_skin):
        view = skin()[self.view_idx]
        radius = (std_lane_width - 1) // 2
        if type(self.hand) != type(None):
            if self.hand:
                label = "R"
            else:
                label = "L"
            view = view[:radius] + label + view[radius + 1:]
        return view
    
    def view_layer(self, skin: ViewSkin = default_skin):
        key_range = lane_range(self.lane)
        view = self.get_view(skin)
        def layer(idx):
            _, p = idx
            if key_range[0] <= p and p < key_range[1]:
                return view[p - key_range[0]]
        return layer

class DirectView(Direct, LayerView):
    def __init__(self, direct, b2l) -> None:
        Direct.__init__(self, beat = direct.beat, lane = direct.lane, dir = direct.dir, len = direct.len)
        self.line = int(b2l(direct.beat))
        self.hand = direct.hand
        self.ocp_lines = [self.line]
        self.view_idx = self.dir + "_" + str(self.len)
    
    def get_view(self, skin: ViewSkin = default_skin):
        view = skin()[self.view_idx]
        radius = (std_lane_width - 1) // 2
        if self.dir == "Left":
            radius = - radius - 1
        if type(self.hand) != type(None):
            if self.hand:
                label = "R"
            else:
                label = "L"
            view = view[:radius] + label + view[radius + 1:]
        return view
    
    def view_layer(self, skin: ViewSkin = default_skin):
        key_range = lane_range(self.lane)
        if self.len > 1:
            key_range = key_range[0], key_range[1] + (std_lane_width + 1) * (self.len - 1)
        view = self.get_view(skin)
        def layer(idx):
            _, p = idx
            if key_range[0] <= p and p < key_range[1]:
                return view[p - key_range[0]]
        return layer

class SingleSeireView(LayerGroupView):
    def __init__(self, group: list = []):
        super().__init__(group = group, cache = False)
        self.ocp_lines = []
        for single in group:
            assert isinstance(single, SingleView)
            assert not single.line in self.ocp_lines
            self.ocp_lines.append(single.line)
    
    def view_layer(self, skin: ViewSkin = default_skin):
        def layer(idx):
            l, _ = idx
            i = self.ocp_lines.index(l)
            return self.layer_group[i].view_layer(skin)(idx)
        return layer

class LongBgView(LayerView):
    def __init__(self, touch: Single, release: Single, b2l, l2b):
        super().__init__()
        assert release.beat > touch.beat
        self.touch = touch
        self.release = release
        self.l2b = l2b
        self.ocp_lines = [int(l) for l in range(
            int(b2l(touch.beat)), 
            int(b2l(release.beat)))]
        self.b2l = self.get_l_b_func()
    
    def get_l_b_func(self):
        return lambda b : (b - self.touch.beat) / (self.release.beat - self.touch.beat) * (self.release.lane - self.touch.lane) + float(self.touch.lane)
    
    def line2lane(self, line):
        lane = self.b2l(self.l2b(line))
        if lane < 0.:
            return 0.
        elif lane > 6.:
            return 6.
        else:
            return lane
    
    def view_layer(self, skin: ViewSkin = default_skin):
        line2range = lambda line: lane_range(self.line2lane(line))
        view = skin()["Hold_body"]
        def layer(idx):
            l, p = idx
            try:
                node_range = line2range(float(l))
                if node_range[0] <= p and p < node_range[1]:
                    return view[p - node_range[0]]
            except:
                return None
        return layer

class SlideBgView(LongBgView):
    def __init__(self, touch: Single, release: Single, b2l, l2b, slides = [], method = "cubic"):
        self.slides = slides
        self.method = method
        super().__init__(touch = touch, release = release, b2l = b2l, l2b = l2b)
        
    def get_l_b_func(self):
        if len(self.slides) == 0:
            return super().get_l_b_func
        else:
            nodes = [self.touch] + self.slides + [self.release]
            return interp1d(
                x = array([node.beat for node in nodes]), 
                y = array([node.lane for node in nodes]), 
                kind = self.method)

class HoldBgView(Hold, LayerGroupView):
    def __init__(self, hold: Hold, b2l, l2b, method = "cubic") -> None:
        Hold.__init__(self, notes = [hold.touch] + hold.slides + [hold.release])
        
        spr_slides = [[self.touch]]
        for node in self.slides:
            spr_slides[-1].append(node)
            if node.visible:
                spr_slides.append([node])
        spr_slides[-1].append(self.release)

        long_bg_view_list = []
        for group in spr_slides:
            if len(group) == 2:
                long_bg_view_list.append(LongBgView(group[0], group[-1], b2l, l2b))
            else:
                long_bg_view_list.append(SlideBgView(group[0], group[-1], b2l, l2b, 
                    slides = group[1:-1], method = method))
        
        LayerGroupView.__init__(self, long_bg_view_list)

class HoldView(Hold, LayerGroupView):
    def __init__(self, hold: Hold, b2l, l2b, method = "cubic") -> None:
        node_group = [hold.touch] + hold.slides + [hold.release]
        Hold.__init__(self, notes = node_group)

        single_seire = [
            SingleView(hold.touch, b2l, False)] + [
            SingleView(node, b2l) for node in hold.slides if node.visible] + [
            SingleView(hold.release, b2l, True)]
        single_seire_view = SingleSeireView(single_seire)
        hold_bg_view = HoldBgView(hold, b2l, l2b, method)

        LayerGroupView.__init__(self, [single_seire_view, hold_bg_view])

class SimoBgView(Simo, LayerView):
    def __init__(self, simo: Simo, b2l) -> None:
        Simo.__init__(self, obj1 = simo.obj1, obj2 = simo.obj2, 
            beat = simo.beat, lane = simo.lane)
        self.line = int(b2l(self.beat))
        self.ocp_lines = [self.line]
    
    def view_layer(self, skin: ViewSkin = default_skin):
        radius = (std_lane_width - 1) // 2
        simo_range = lane_range(self.lane[0])[0] + radius, lane_range(self.lane[1])[0] + radius
        def layer(idx):
            _, p = idx
            if simo_range[0] <= p and p < simo_range[1]:
                return skin()["Simo_link"]
        return layer

class LineView(LayerGroupView):
    def __init__(self, line, touches = [], simo = None, bg = None):
        self.line = line
        self.touches = touches
        self.simo = simo
        self.bg = ClearChartView(line) if type(bg) == type(None) else bg
        self.__verify()
        self.__construct()
    
    def __verify(self):
        for obj in self.touches:
            assert type(obj) in [SingleView, DirectView, HoldView], "交互图层对象类型为%s"%(str(type(obj)))
        assert type(self.simo) in [SimoBgView, type(None)], "同时线图层对象类型为%s，应为%s"%(str(type(self.simo)), str(SimoBgView))
        assert type(self.bg) == ClearChartView, "背景图层对象类型为%s，应为%s"%(str(type(self.bg)), str(ClearChartView))

        assert len(self.touches) <= 2, "一行内最多有2个键对象，当前有%i"%(len(self.touches))
        
        if type(self.simo) == SimoBgView:
            assert len(self.touches) == 2, "仅在有%i个交互对象时可以设置同时线，当前有%i个对象"%(2, len(self.touches))
        
        for obj in self.touches + [self.simo] if not type(self.simo) == type(None) else self.touches:
            assert self.line in obj.ocp_lines, "当前图层为第%i行可视化，但对象包含%s行"%(self.line, str(obj.ocp_lines))
        
    def __construct(self):
        group = []
        if len(self.touches) > 0:
            group += self.touches
        if not type(self.simo) == type(None):
            group.append(self.simo)
        group.append(self.bg)
        super().__init__(group = group, cache = False)
        self.ocp_lines = [self.line]
        self.process_cache()

class ChartView(LayerGroupView):
    def __init__(self, chart: Chart, bps = None, curve_method = "cubic"):
        self.chart = chart
        self.method = curve_method

        self.set_lpb(bps)
        logging.info("谱面初始化完成！")
        self.process()

        self.line_views = []
        self.single_views = []
        self.direct_views = []
        self.hold_views = []
        for l in range(self.num_line):
            if l % 1000 == 0 or l == self.num_line - 1:
                logging.info("%i/%i行构建完成"%(l, self.num_line))
            self.line_views.append(self.get_line_view(l))

    def set_lpb(self, bps):
        assert bps in [1, 2, 4, None], "每秒近似拍数须为1、2、4，输入的%s不合法"%(str(bps))
        if type(bps) == type(None):
            expand = self.chart.bpm / 60.
            if expand < 1.41:
                self.lpb = 64
            elif expand > 3.5:
                self.lpb = 16
            else: 
                self.lpb = 32
        else: 
            self.lpb = 64 // bps
        
        assert self.chart.get_min_retouch()[0][0] * self.lpb >= 1, "谱面按键过于密集，无法可视化"

        self.set_trans()
        self.num_line = int(self.lpb * self.chart.get_len()) + 1
        
        self.line_repo = []
        for _ in range(self.num_line): self.line_repo.append({
            "touch": [], 
            "simo": None})

    def set_trans(self):
        self.b2l = lambda beat: 1. * beat * self.lpb
        self.l2b = lambda line: 1. * line / self.lpb
    
    def process(self):
        for single in self.chart.keys["Single"] + self.chart.keys["Flick"]:
            single_view = SingleView(single, self.b2l)
            l = single_view.ocp_lines[0]
            assert len(self.line_repo[l]["touch"]) < 2, "%i行按键过多"%(l)
            self.line_repo[l]["touch"].append(single_view)
        logging.info("单键与划键加载完成！")
        
        for direct in self.chart.keys["Direct"]:
            direct_view = DirectView(direct, self.b2l)
            l = direct_view.ocp_lines[0]
            assert len(self.line_repo[l]["touch"]) < 2, "%i行按键过多"%(l)
            self.line_repo[l]["touch"].append(direct_view)
        logging.info("定向划键加载完成！")
        
        for hold in self.chart.keys["Hold"]:
            hold_view = HoldView(hold, self.b2l, self.l2b, self.method)
            for l in hold_view.ocp_lines:
                assert len(self.line_repo[l]["touch"]) < 2, "%i行按键过多"%(l)
                self.line_repo[l]["touch"].append(hold_view)
        logging.info("长键加载完成！")
        
        for simo in self.chart.simo:
            simo_line = SimoBgView(simo, self.b2l)
            self.line_repo[simo_line.ocp_lines[0]]["simo"] = simo_line
        logging.info("同时线加载完成！")
        
        self.bg_chart = ClearChartView(self.num_line)
        self.bg_char = " "
        logging.info("谱面背景加载完成！")
    
    def get_line_view(self, line):
        return LineView(line, self.line_repo[line]["touch"], self.line_repo[line]["simo"], self.bg_chart)

    def view_layer(self, skin: ViewSkin = default_skin):
        def layer(idx):
            l, _ = idx
            line_view = self.line_views[l]
            return line_view.view_layer(skin)(idx)
        return layer
    
    def get_line(self):
        layer = self.view_layer()
        text = []
        for l in range(self.num_line):
            line_str = ""
            for p in range((std_lane_width + 1) * 7 + 1):
                rep_char = layer((l, p))
                if type(rep_char) == type(None) or rep_char == "#":
                    line_str += self.bg_char
                else:
                    line_str += rep_char
            text.append(line_str)
        return text
