from utils.decorators import attr_check
from utils.units import Time, Velocity, Acceleration, Jerk


@attr_check
class Config:

    dt = Time
    max_velocity = Velocity
    max_acceleration = Acceleration
    max_jerk = Jerk
    sample_count = int

    def __init__(self, **kwargs):
        self.dt = Time(kwargs['dt'])
        self.max_velocity = Velocity(kwargs['max_velocity'])
        self.max_acceleration = Acceleration(kwargs['max_acceleration'])
        self.max_jerk = Jerk(kwargs['max_jerk'])
        self.sample_count = int(kwargs['sample_count'])

        self.__dict__.update(kwargs)
