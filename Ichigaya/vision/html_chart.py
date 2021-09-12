from scipy.interpolate.interpolate import interp1d
from Ichigaya.chart import key
from ..chart import Single, Flick, Hold, Direct, Simo, Chart, slide
import json
import codecs
from os.path import dirname
from scipy.interpolate import interp1d
from numpy import array

current_path = dirname(__file__)
std_lane_width = 15
l2i = lambda lane: int(1. + (std_lane_width + 1.) * lane)
lane_range = lambda lane: (l2i(lane), l2i(lane) + std_lane_width)

class ViewSkin():
    key_names = ["size"], ["single", "Flick", "Hold_touch", "Hold_release", "Hold_flick", "Hold_body", "Hold_node", "Left_1", "Right_1"], ["Left_2", "Right_2"], ["Left_3", "Right_3"]
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

        for i, group in enumerate(self.key_names[1:]):
            std_len = std_lane_width * (i + 1) + i
            for obj in group:
                act_len = len(self.json[obj])
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
    def __init__(self, group: list = []):
        for layer_view in group:
            assert isinstance(layer_view, LayerView)
        super().__init__()
        self.layer_group = group

        for layer_view in group:
            for line in layer_view.ocp_lines:
                if not line in self.ocp_lines:
                    self.ocp_lines.append(line)
        self.ocp_lines = sorted(self.ocp_lines)
    
    def view_layer(self):
        def layer(idx):
            for layer_view in self.layer_group:
                view = layer_view.view_layer()(idx)
                if type(view) != type(None) and view != "#":
                    break
            return view
        return layer

class ClearChartView(LayerView):
    def __init__(self, length):
        self.ocp_lines = [i for i in range(length)]

    def view_layer(self):
        def layer(idx):
            _, p = idx
            if p % (std_lane_width + 1) == 0:
                return "|"[0]
            return None
        return layer

class SingleView(Single, LayerView):
    def __init__(self, single, b2l, hold_rls = None) -> None:
        Single.__init__(self, beat = single.beat, lane = single.lane)
        self.line = b2l(single.beat)
        self.hand = single.hand
        self.ocp_lines = [self.line]
        if type(hold_rls) == type(None):
            if type(single) == Single:
                self.view_idx = "Single"
            elif type(single) == Flick:
                self.view_idx = "Flick"
            else:
                self.view_idx = "Hold_node"
        else:
            assert type(single) != slide
            if hold_rls:
                self.view_idx = "Hold_release" if type(single) == Single else "Hold_flick"
            else: 
                assert type(single) == Single
                self.view_idx = "Hold_touch"
    
    def get_view(self, skin: ViewSkin = default_skin):
        org_view = skin()[self.view_idx]
        radius = (std_lane_width - 1) // 2
        if type(self.hand) != type(None):
            if self.hand:
                label = "R"
            else:
                label = "L"
            view = org_view[:radius] + label + org_view[radius + 1:]
        return view
    
    def view_layer(self):
        key_range = lane_range(self.lane)
        view = self.get_view()
        def layer(idx):
            l, p = idx
            if l == self.line:
                if key_range[0] <= p and p < key_range[1]:
                    return view[p - key_range[0]]
            return None
        return layer

class DirectView(Direct, LayerView):
    def __init__(self, direct, b2l) -> None:
        Direct.__init__(self, beat = direct.beat, lane = direct.lane, dir= direct.dir, len = direct.len)
        self.line = b2l(direct.beat)
        self.hand = direct.hand
        self.ocp_lines = [self.line]
        self.view_idx = self.dir + "_" + str(self.len + 1)
    
    def get_view(self, skin: ViewSkin = default_skin):
        org_view = skin()[self.view_idx]
        radius = (std_lane_width - 1) // 2
        if self.dir == "Left":
            radius = - radius - 1
        if type(self.hand) != type(None):
            if self.hand:
                label = "R"
            else:
                label = "L"
            view = org_view[:radius] + label + org_view[radius + 1:]
        return view
    
    def view_layer(self):
        key_range = lane_range(self.lane)
        if self.len > 1:
            key_range[1] += (std_lane_width + 1) * (self.len - 1)
        view = self.get_view()
        def layer(idx):
            l, p = idx
            if l == self.line:
                if key_range[0] <= p and p < key_range[1]:
                    return view[p - key_range[0]]
            return None
        return layer

class SingleSeireView(LayerGroupView):
    def __init__(self, group: list = []):
        super().__init__(group = group)
        self.ocp_lines = []
        for single in group:
            assert isinstance(single, SingleView)
            assert not single.line in self.ocp_lines
            self.ocp_lines.append(single.line)
    
    def view_layer(self):
        def layer(idx):
            l, _ = idx
            if l in self.ocp_lines: 
                i = self.ocp_lines.index(l)
                return self.layer_group[i].view_layer()(idx)
            return None
        return layer

class LongBgView(LayerView):
    def __init__(self, touch: Single, release: Single, l2b, slides = [], method = "cubic"):
        super().__init__()
        assert release.beat > touch.beat
        self.touch = touch
        self.release = release
        self.slides = slides
        self.l2b = l2b
        self.ocp_lines = [l for l in range(touch.beat, release.beat)]
        self.method = method
        self.b2l = self.get_l_b_func()
    
    def get_l_b_func(self):
        if len(self.slides) == 0:
            return lambda b : (b - self.touch.beat) / (self.release.beat - self.touch.beat) * (self.release.lane - self.touch.lane) + self.touch.lane
        else:
            nodes = [self.touch] + self.slides + [self.release]
            return interp1d(
                x = array([node.beat for node in nodes]), 
                y = array([node.lane for node in nodes]), 
                kind = self.method)
    
    def line2lane(self, line):
        lane = self.b2l(self.l2b(line))
        if lane < 0.:
            return 0
        elif lane > 6.:
            return 6
        else:
            return lane
    
    def view_layer(self, skin: ViewSkin = default_skin):
        line2range = lambda line: lane_range(self.line2lane(line))
        view = skin()["Hold_node"]
        def layer(idx):
            l, p = idx
            if l in self.ocp_lines:
                node_range = line2range(l)
                if node_range[0] <= p and p < node_range[1]:
                    return view[p - node_range[0]]
            return None
        return layer
