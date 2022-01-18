from ..chart import Chart, Single, Flick, Hold, Direct
from .. utils import id_name_trans
import json, codecs
import re
import os



n = 2 ** 4 * 3
prior = lambda obj: (type(obj) in [Single, Flick, Direct]) + (type(obj) in [Flick, Direct]) + (type(obj) == Direct)



def to_stgs(chart: Chart, filename = None): 
    filename = str(chart.get()[0]) + "-" + id_name_trans(chart.get()[0]) + "-" + chart.get()[1]if filename is None else filename
    filename = re.sub(" ", "_", filename)
    filename = re.sub("[\/:*?|<>\"]", "", filename)
    with codecs.open(filename + ".json", "w") as f:
        f.write(json.dumps(get_stgs(chart)))
    
    if os.path.exists(filename + ".stgs"): 
        os.remove(filename + ".stgs")
    os.rename(filename + ".json", filename + ".stgs")



def get_stgs(chart: Chart): 
    return {
    "meta": {},
    "notes": get_stgs_chart(chart), 
    "bpm": get_stgs_stamps(chart), 
    "offset": 0, 
    "editor": {
        "rowheight": 240,
        "division": 4,
        "tool": 0,
        "maxrow": 247,
        "noteId": get_stgs_chart(chart)[-1]["id"],
        "soundeffect": True,
        "auto": True}}

def get_stgs_chart(chart: Chart): 
    notes = []
    id = 1001
    for key in get_all(chart): 
        if type(key) == Single: 
            notes.append(single_trans(key, id))
            id += 1
        elif type(key) == Flick: 
            notes.append(flick_trans(key, id))
            id += 1
        elif type(key) == Direct: 
            notes.append(direct_trans(key, id))
            id += 1
        else: 
            notes += hold_trans(key, id)
            id = notes[-1]["id"] + 1
    return notes

def get_stgs_stamps(chart: Chart): 
    stms = []
    for obj in chart.json:
        if obj["type"] == "BPM":
            stms.append({
                "value": obj["bpm"], 
                "time": beat_trans(obj["beat"] + 1)})
    return stms


def gcd(a, b): 
    if a < b: 
        a, b = b, a
    while b: 
        a, b = b, a % b
    return a

def beat_trans(beat): 
    _int = int(beat)
    _dci = beat - _int
    if _dci < 1e-3: 
        return [_int, 0, 4]
    _dvi = int(_dci * n)
    _g = gcd(_dvi, n)
    if int(n / _g) < 4: _g /= 2
    return[_int, int(_dvi / _g), int(n / _g)]



def single_trans(key: Single, id): 
    return {
        "time": beat_trans(key.beat + 1),
        "track": key.lane,
        "type": 0,
        "id": id}

def flick_trans(key: Flick, id): 
    js = single_trans(key, id)
    js["type"] = 1
    return js

def direct_trans(key: Direct, id): return flick_trans(key, id)

def hold_trans_single(s: Single, e: Single, id): 
    return {
        "type": 2,
        "time": beat_trans(s.beat + 1), 
        "track": s.lane,
        "endtrack": e.lane,
        "endtime": beat_trans(e.beat + 1), 
        "headtype": 2,
        "tailtype": 2 - int(type(e) == Flick),
        "prev": id - 1,
        "next": id + 1,
        "id": id}

def hold_trans(key: Hold, id): 
    slides = [slide for slide in key.slides if slide.visible]
    if slides == []: 
        js = hold_trans_single(key.touch, key.release, id)
        js["prev"], js["next"] = 0, 0
        js["headtype"], js["tailtype"] = 0, 0 if js["tailtype"] == 2 else js["tailtype"]
        return [js]
    js = [hold_trans_single(key.touch, slides[0], id)]
    for i in range(len(slides) - 1): 
        id += 1
        js.append(hold_trans_single(slides[i], slides[i + 1], id))
    id += 1
    js.append(hold_trans_single(slides[-1], key.release, id))
    js[0]["prev"], js[-1]["next"] = 0, 0
    js[0]["headtype"], js[-1]["tailtype"] = 0, 0 if js[-1]["tailtype"] == 2 else js[-1]["tailtype"]
    return js



def get_all(chart: Chart): 
    return sorted(chart.keys["Single"] + chart.keys["Flick"] + chart.keys["Hold"] + chart.keys["Direct"], key = lambda k: get_st(k) + prior(k) * 1e-3)

def get_st(obj): 
    assert type(obj) in [Single, Flick, Hold, Direct]
    if type(obj) == Hold: 
        return obj.touch.beat
    return obj.beat

