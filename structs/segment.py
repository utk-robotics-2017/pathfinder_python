from util.units import Distance, Velocity, Acceleration, Jerk, Time
from util.decorators import attr_check, type_check


@attr_check
class Segment:
    time = Time
    distance = Distance
    velocity = Velocity
    acceleration = Acceleration
    jerk = Jerk

    @type_check
    def __init__(self, **kwargs):
        self.time = 0
        self.distance = 0
        self.velocity = 0
        self.acceleration = 0
        self.jerk = 0

        self.__dict__.update(kwargs)
