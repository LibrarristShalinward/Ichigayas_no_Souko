


class Note:
    def __init__(self, beat = 0, lane = 0, json = None) -> None:
        if json != None:
            self.beat
        else:
            self.beat = float(beat)
            self.lane = float(lane)



class Single(Note):
    def __init__(self, beat = 0, lane = 0) -> None:
        super().__init__(beat = beat, lane = lane)
        self.lane = int(self.lane)
        self.hand = None

class Flick(Single):
    def __init__(self, beat = 0, lane = 0) -> None:
        super().__init__(beat = beat, lane = lane)
        self.dir = None

class Direct(Flick):
    def __init__(self, beat = 0, lane = 0, dir = "Left", len = 1) -> None:
        super().__init__(beat=beat, lane=lane)
        self.dir = dir
        self.len = len


class slide(Note):
    def __init__(self, beat = 0, lane = 0, visible = True) -> None:
        super().__init__(beat = beat, lane = lane)
        self.visible = visible
        if visible: self.lane = int(self.lane)

class Hold:
    def __init__(self, notes = [Single(), Single()]) -> None:
        self.touch = notes[0]
        self.release = notes[-1]
        self.hand = self.touch.hand
        self.slides = notes[1:-1]
        self.flick = type(self.release) == Flick