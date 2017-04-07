class Segment:
    def __init__(self, **kwargs):
        self.time = 0
        self.distance = 0
        self.velocity = 0
        self.acceleration = 0
        self.jerk = 0

        self.__dict__.update(kwargs)