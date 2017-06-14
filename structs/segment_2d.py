from utils.units import Distance, Angle
from utils.decorators import attr_check, type_check


@attr_check
class Segment2D:
    ''' A 2D representation of a segment.

        Attributes
        ----------
        x : Distance
            The x coordinate of the start of this segment
        y : Distance
            The y coordinate of the start of this segment
        angle : Angle
            The angle the robot should be facing at the start of this segment
    '''
    x = Distance
    y = Distance
    angle = Angle

    def __init__(self, **kwargs):
        self.x = kwargs.get('x', Distance(0))
        self.y = kwargs.get('y', Distance(0))
        self.angle = kwargs.get('angle', Angle(0))

    @type_check
    def toWs(self) -> str:
        return "{:.2f},{:2f},{:2f}".format(self.x.to(Distance.inch),
                                           self.y.to(Distance.inch),
                                           self.angle.to(Angle.degree))
