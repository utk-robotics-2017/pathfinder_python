from utils.decorators import attr_check, type_check
from utils.units import Distance, Angle


@attr_check
class Waypoint:
    x = Distance
    y = Distance
    angle = Angle

    @type_check
    def __init__(self, x: Distance, y: Distance, angle: Angle):
        self.x = x
        self.y = y
        self.angle = angle
