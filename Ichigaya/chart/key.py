


def json2key(json):
    if not "type" in json.keys():
        return slide(json)
    if json["type"] == "Single":
        if "flick" in json.keys() and json["flick"]:
            return Flick(json)
        else:
            return Single(json)
    if json["type"] == "Directional":
        return Direct(json)
    if json["type"] in ["Long", "Slide"]:
        return Hold(json)

class Note:
    def __init__(self, json = None, beat = 0, lane = 0) -> None:
        if json != None:
            self.json_set(json)
        else:
            self.beat = float(beat)
            self.lane = float(lane)
    
    def json_set(self, json):
        self.beat = float(json["beat"])
        self.lane = float(json["lane"])

class directionalNote(Note):
    def __init__(self, json = None, beat = 0, lane = 0) -> None:
        super().__init__(json = json, beat = beat, lane = lane)
        self.hand = None
    
    def set_hand(self, hand = None):
        if hand is not None and self.hand is not None:
            assert hand == self.hand
        else:
            self.hand == hand

class Single(directionalNote):
    def __init__(self, json = None, beat = 0, lane = 0) -> None:
        super().__init__(beat=beat, lane=lane, json=json)
        self.lane = int(self.lane)

class Flick(Single):
    def __init__(self, json = None, beat = 0, lane = 0) -> None:
        self.dir = None
        super().__init__(beat = beat, lane = lane, json = json)

class Direct(Flick):
    def __init__(self, json = None, 
        beat = 0, lane =0, 
        dir = "Left", len = 1) -> None:
        super().__init__(beat = beat, lane = lane, json = json)
        if json == None:
            self.dir = dir
            self.len = len
    
    def json_set(self, json):
        super().json_set(json)
        self.dir = json["direction"]
        self.len = json["width"]


class slide(directionalNote):
    def __init__(self, json = None, beat = 0, lane = 0, visible = True) -> None:
        super().__init__(beat=beat, lane=lane, json=json)
        if json == None:
            self.visible = visible
        if self.visible: 
            self.lane = int(self.lane)
    
    def json_set(self, json):
        super().json_set(json)
        if "hidden" in json.keys() and json["hidden"]:
            self.visible = False
        else: self.visible = True

class Hold:
    def __init__(self, json = None, notes = [Single(), Single()]) -> None:
        if json != None: self.json_set(json)
        else:
            self.touch = notes[0]
            self.release = notes[-1]
            self.slides = notes[1:-1]
            self.hand = self.touch.hand
        self.flick = type(self.release) == Flick
    
    def json_set(self, json):
        self.touch = Single(json["connections"][0])
        if "flick" in json["connections"][-1].keys() and json["connections"][-1]["flick"]:
            self.release = Flick(json["connections"][-1])
        else:
            self.release = Single(json["connections"][-1])
        self.slides = []
        for obj in json["connections"][1:-1]:
            self.slides.append(slide(obj))
    
    def set_hand(self, hand = None):
        self.touch.set_hand(hand)
        for s in self.slides:
            s.set_hand(hand)
        self.release.set_hand(hand)

class Simo():
    def __init__(self, obj1 = None , obj2 = None, beat = 0, lane = (0, 0)) -> None:
        self.beat = beat
        if lane[0] < lane[1]:
            self.obj1, self.obj2 = obj1, obj2
            self.lane = lane
        else:
            self.obj1, self.obj2 = obj2, obj1
            self.lane = lane[1], lane[0]
    
    def is_obj1(self, note):
        if isinstance(note):
            return self.is_obj1((type(note), None, note.beat, note.lane))
        else:
            assert type(note) == tuple
            return note == self.obj1 + (self.beat, self.lane[0])
    
    def is_obj2(self, note):
        if isinstance(note):
            return self.is_obj2((type(note), None, note.beat, note.lane))
        else:
            assert type(note) == tuple
            return note == self.obj2 + (self.beat, self.lane[1])
    
    def is_included(self, note):
        return self.is_obj1(note) or self.is_obj2(note)
    
    def set_hand(self):
        self.obj1.set_hand("Left")
        self.obj2.set_hand("Right")