


just_len = 10

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
    
    def __str__(self) -> str:
        return ("第%.2f拍"%(self.beat)).ljust(just_len) + ("第%i轨"%(self.lane)).ljust(just_len)

class directionalNote(Note):
    def __init__(self, json = None, beat = 0, lane = 0) -> None:
        super().__init__(json = json, beat = beat, lane = lane)
        self.hand = None
    
    def set_hand(self, hand = None):
        if hand is not None and self.hand is not None:
            assert hand == self.hand
        else:
            self.hand = hand
    
    def __str__(self) -> str:
        if self.hand:
            if self.hand == "Left":
                return super().__str__() + "左手".ljust(just_len)
            else:
                return super().__str__() + "右手".ljust(just_len)
        else:
            return super().__str__()

class Single(directionalNote):
    def __init__(self, json = None, beat = 0, lane = 0) -> None:
        super().__init__(beat=beat, lane=lane, json=json)
        self.lane = int(self.lane)
    
    def __str__(self) -> str:
        return super().__str__()
    
    def __repr__(self) -> str:
        return "单键：".ljust(just_len) + self.__str__()

class Flick(Single):
    def __init__(self, json = None, beat = 0, lane = 0) -> None:
        self.dir = None
        super().__init__(beat = beat, lane = lane, json = json)
    
    def __str__(self) -> str:
        return "滑键：".ljust(just_len) + super().__str__()

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
    
    def __str__(self) -> str:
        return "滑" + super().__str__()[1:] + ("方向：%s"%("左" if self.dir == "Left" else "右")).ljust(just_len) + ("长度:%i"%(self.len)).ljust(just_len)


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
    
    def __str__(self) -> str:
        return super().__str__()

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
    
    def __str__(self) -> str:
        all_str = "=====\n长键：\n"
        all_str += self.touch.__str__() + "\n"
        for s in self.slides:
            all_str += s.__str__() + "\n"
        all_str += self.release.__str__()
        return all_str + "\n====="

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
        self.obj1[-1].set_hand("Left")
        self.obj2[-1].set_hand("Right")
    
    def __str__(self) -> str:
        return "----\n同时对象：\n" + self.obj1.__str__() + "\n" + self.obj2.__str__() + "\n-----"