import math
from mathutil import bound_radians
from enum import Enum
from structs.spline import Spline


class FitType(Enum):
    CUBIC = 0
    QUINTIC = 1


class SplineGenerator:
    def __init__(self, fit_type=FitType.CUBIC):
        self.fit_type = fit_type

    def fit(self, a, b):
        if self.fit_type == FitType.CUBIC:
            return self.cubic_fit(a, b)
        elif self.fit_type == FitType.QUINTIC:
            return self.quintic_fit(a, b)

    def cubic_fit(self, a, b):
        s = self.prepare(a, b)

        a0_delta = math.tan(bound_radians(a.angle - s.angle_offset))
        a1_delta = math.tan(bound_radians(b.angle - s.angle_offset))

        s.a = 0
        s.b = 0
        s.c = (a0_delta + a1_delta) / (s.knot_distance * s.knot_distance)
        s.d = -(2 * a0_delta + a1_delta) / s.knot_distance
        s.e = a0_delta

        return s

    def quintic_fit(self, a, b):
        s = self.prepare(a, b)

        a0_delta = math.tan(bound_radians(a.angle - s.angle_offset))
        a1_delta = math.tan(bound_radians(b.angle - s.angle_offset))

        d = s.knot_distance

        s.a = -(3 * (a0_delta + a1_delta)) / (d * d * d * d)
        s.b = (8 * a0_delta + 7 * a1_delta) / (d * d * d)
        s.c = -(6 * a0_delta + 4 * a1_delta) / (d * d)
        s.d = 0
        s.e = a0_delta

        return s

    def prepare(self, a, b):
        s = Spline()
        s.x_offset = a.x
        s.y_offset = a.y

        delta = math.sqrt((b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a. y))
        s.knot_distance = delta
        s.angle_offset = math.atan2(b.y - a.y, b.x - a.x)
        return s
