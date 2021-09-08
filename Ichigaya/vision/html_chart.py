from Ichigaya.chart import key
from ..chart import Single, Hold, Direct, Simo, Chart
import json
import codecs
from os.path import dirname

current_path = dirname(__file__)
std_lane_width = 15
lane_start_idx = [1]
for i in range(1, 7):
    lane_start_idx.append(lane_start_idx[-1] + std_lane_width + 1)
lane_range = lambda lane: (lane_start_idx[lane], lane_start_idx[lane] + std_lane_width)

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
                if type(view) != type(None):
                    return view
            return None
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
            self.view_idx = "Single" if type(single) == Single else "Flick"
        else:
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