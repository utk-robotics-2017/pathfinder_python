import numpy as np
import math
from .spline import Spline, SplineType
from structs.spline_coord import SplineCoord
from structs.waypoint import Waypoint
from utils.units import Time, Distance, Velocity, Angle
from utils.decorators import attr_check, type_check


@attr_check
class Hermite(Spline):
    '''
        ANGLE_AUTO will only work using the Pathfinder::Spline::hermite() namespace method, not
        in the constructor or configure() method of Pathfinder::Spline::Hermite
        Furthermore, ANGLE_AUTO will work on every waypoint that is NOT the first
        waypoint in the array, as the auto-generated angle is based on the slope of the
        line joining waypoint and waypoint-1
    '''
    ANGLE_AUTO = 100000
    start = Waypoint
    end = Waypoint
    x_offset = Distance
    y_offset = Distance
    angle_offset = Angle
    hyp_distance = Distance
    tangent0 = float
    tangent1 = float
    a = Distance
    b = Distance
    last_arc_calc = Distance
    last_arc_samples = int

    @type_check
    def __init__(self, type_: int, start: Waypoint, end: Waypoint):
        self.type_ = type_
        self.start = start
        self.end = end

        self.x_offset = start.x
        self.y_offset = start.y

        dy = end.y - start.y
        dx = end.x - start.x

        self.angle_offset = Angle(math.atan2(dy, dx) * Angle.rad)
        self.hyp_distance = Distance(math.sqrt(dx.base_value ** 2 + dy.base_value ** 2))
        self.tangent0 = math.tan(start.angle - self.angle_offset)
        self.tangent1 = math.tan(end.angle - self.angle_offset)
        self.a = self.tangent0 * self.hyp_distance
        self.b = self.tangent1 * self.hyp_distance

        # Cache the arc calc to save time
        self.last_arc_calc = Distance()
        self.last_arc_calc_samples = 0

    @type_check
    def calculate(self, t: Time) -> SplineCoord:
        coord = SplineCoord(time=t)
        x = Distance(self.hyp_distance() * t())
        y = Distance()
        if self.type_ == SplineType.HERMITE_CUBIC:
            y = Distance(((self.tangent0 + self.tangent1) * self.hyp_distance() * t() ** 3)
                         + (-(2 * self.tangent0 + self.tangent1) * self.hyp_distance() * t() ** 2)
                         + self.tangent0 * self.hyp_distance() * t())
        elif self.type_ == SplineType.HERMITE_QUINTIC:
            y = Distance((-3 * (self.tangent0 + self.tangent1)) * self.hyp_distance() * t() ** 5
                          + (8 * self.tangent0 + 7 * self.tangent1) * self.hyp_distance() * t() ** 4
                          + (-(6 * self.tangent0 + 4 * self.tangent1)) * self.hyp_distance() * t() ** 3
                          + self.tangent0 * self.hyp_distance() * t())

        # Translate back to global
        coord.x = x * math.cos(self.angle_offset) - y * math.sin(self.angle_offset) + self.x_offset
        coord.y = x * math.sin(self.angle_offset) - y * math.cos(self.angle_offset) + self.y_offset

        @type_check
        def bound_radians(angle: Angle) -> Angle:
            new_angle = Angle(math.fmod(angle.to(Angle.rad), 2 * 3.14159265) * Angle.rad)
            if new_angle < 0:
                new_angle = Angle(2 * 3.14159265 * Angle.rad) + new_angle
            return new_angle

        coord.angle = bound_radians(Angle(math.atan(self.derive(t))) + self.angle_offset)

        return coord

    @type_check
    def deriv(self, t: Time) -> Velocity:
        # x = self.hyp_distance * t
        if self.type_ == SplineType.HERMITE_CUBIC:
            return Velocity((3 * (self.tangent0 + self.tangent1) * t() ** 2) +
                            (2 * -(2 * self.tangent0 + self.tangent1) * t()
                            + self.tangent0))
        elif self.type_ == SplineType.HERMITE_QUINTIC:
            return Velocity(5 * (-(3*(self.tangent0 + self.tangent1))) * t() ** 4
                            + 4 * (8 * self.tangent0 + 7 * self.tangent1) * t() ** 3
                            + 3 * (-(6 * self.tangent0 + 4 * self.tangent1)) * t() ** 2
                            + self.tangent0)

    @type_check
    def arc_length(self, samples: list) -> Distance:
        if self.last_arc_calc_samples != samples:
            t = Time(0)
            dt = 1 / samples

            dydt = self.deriv(t)
            integrand = Distance(0)
            arc_length_ = Distance(0)
            last_integrand = Distance(math.sqrt(1 + dydt() ** 2) * dt())

            # [0, 1)
            for t in np.arange(0, 1, dt):
                dydt = self.deriv(t)
                integrand = Distance(math.sqrt(1 + dydt() ** 2) * dt())
                arc_length_ += (integrand + last_integrand) / 2
                last_integrand = integrand
            dydt = self.deriv(1)
            integrand = Distance(math.sqrt(1 + dydt() ** 2) * dt())
            arc_length_ += (integrand + last_integrand) / 2
            last_integrand = integrand

            # last_arc_calc_samples = samples
            last_arc_calc = Distance(self.hyp_distance * arc_length_)
        return last_arc_calc

    @classmethod
    @type_check
    def get_splines(cls, type_: int, waypoints: list) -> list:
        splines = []
        for i in range(len(waypoints) - 1):
            splines.append(Hermite(type_, waypoints[i], waypoints[i + 1]))
        return splines
