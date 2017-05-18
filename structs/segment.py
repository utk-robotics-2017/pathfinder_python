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
        self.time = kwargs.get('time', Time(0))
        self.distance = kwargs.get('distance', Distance(0))
        self.velocity = kwargs.get('velocity', Velocity(0))
        self.acceleration = kwargs.get('acceleration', Acceleration(0))
        self.jerk = kwargs.get('jerk', Jerk(0))
