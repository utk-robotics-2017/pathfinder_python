from utils.decorators import attr_check, type_check
from utils.units import Distance, Angle


@attr_check
class Waypoint:
    x = Distance
    y = Distance
    angle = Angle

    @type_check
    def __init__(self, x: (int, float), y: (int, float), r: (int, float)):
        self.x = Distance(x)
        self.y = Distance(y)
        self.angle = Angle(r)
