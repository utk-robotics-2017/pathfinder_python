class SplineCoord:
    def __init__(self, **kwargs):
        self.time = 0.0
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0
        self.__dict__.update(kwargs)
