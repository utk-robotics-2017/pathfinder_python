from utils.units import Distance, Velocity, Acceleration, Jerk, Time
from utils.decorators import attr_check, type_check


@attr_check
class Segment:
    ''' A single 1D segment in the path traveled.

        Attributes
        ----------
        time : Time
            The time at which this segment should be started
        distance : Distance
            The distance which should have been traveled by the start of this segment
        velocity : Velocity
            The velocity that the robot should have at the start of this segment
        acceleration : Acceleration
            The acceleration that the robot should have at the start of this segment
        jerk : Jerk
            The jerk that the robot should have at the start of this segment

        See Also
        --------
        Segment2D
        CoupledSegment

    '''

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
