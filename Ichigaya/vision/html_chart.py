from ..chart import Single, Hold, Direct, Simo, Chart

class SingleView(Single):
    def __init__(self, single, b2l) -> None:
        super().__init__(beat = 0, lane = single.lane)
        self.line = b2l(single.beat)
        self.hand = single.hand
        self.view_idx = "Single" if type(single) == Single else "Flick"