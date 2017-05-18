from util.units import Distance, Angle
from util.decorators import attr_check, type_check

@attr_check
class Segment2D:
    x = Distance
    y = Distance
    angle = Angle

    def __init__(self, **kwargs):
        self.x = kwargs.get('x', Distance(0))
        self.y = kwargs.get('y', Distance(0))
        self.angle = kwargs.get('angle', Angle(0))