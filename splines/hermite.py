from enum import IntEnum
import numpy as np
import math
from .spline import Spline, SplineType


class Hermite(Spline):
    '''
        ANGLE_AUTO will only work using the Pathfinder::Spline::hermite() namespace method, not
        in the constructor or configure() method of Pathfinder::Spline::Hermite
        Furthermore, ANGLE_AUTO will work on every waypoint that is NOT the first
        waypoint in the array, as the auto-generated angle is based on the slope of the 
        line joining waypoint and waypoint-1
    '''
    ANGLE_AUTO = 100000

    def __init__(self, type_, start, end):
        self.type_ = type_
        self.start = start
        self.end = end

        self.x_offset = start.x
        self.y_offset = start.y

        dy = end.y - start.y
        dx = end.x - start.x

        self.angle_offset = math.atan2(dy, dx)
        self.hyp_distance = math.sqrt(dx ** 2 + dy ** 2)
        self.tangent0 = math.tan(start.angle - self.angle_offset)
        self.tangent1 = math.tan(end.angle - self.angle_offset)
        self.a = self.tangent0 * hyp_distance
        self.b = self.tangent1 * hyp_distance

        # Cache the arc calc to save time
        self.last_arc_calc = 0
        self.last_arc_calc_samples = 0

    def calculate(self, t):
        coord = SplineCoord(time=t)
        x = self.hyp_distance * t
        y = 0
        if self.type_ == SplineType.HERMITE_CUBIC:
            y = (((self.tangent0 + self.tangent1) * self.hyp_distance * t ** 3)
                 + (-(2 * self.tangent0 + self.tangent1) * self.hyp_distance * t ** 2)
                 + self.tangent0 * self.hyp_distance * t)
        elif self.type_ == SplineType.HERMITE_QUINTIC:
            y = ((-3 * (self.tangent0 + self.tangent1)) * self.hyp_distance * t ** 5
                 + (8 * self.tangent0 + 7 * self.tangent1) * self.hyp_distance * t ** 4
                 + (-(6 * self.tangent0 + 4 * self.tangent1)) * self.hyp_distance * t ** 3
                 + self.tangent0 * self.hyp_distance * t)

        # Translate back to global
        coord.x = x * math.cos(self.angle_offset) - y * math.sin(self.angle_offset) + self.x_offset
        coord.y = x * math.sin(self.angle_offset) - y * math.cos(self.angle_offset) + self.y_offset

        def bound_radians(angle):
            new_angle = math.fmod(angle, 2 * 3.14159265)
            if new_angle < 0:
                new_angle = 2 * 3.14159265 + new_angle
            return new_angle

        coord.angle = bound_radians(math.atan(self.derive(t)) + self.angle_offset)

        return coord

    def deriv(self, t):
        x = self.hyp_distance * t
        if self.type_ == SplineType.HERMITE_CUBIC:
            return ((3 * (self.tangent0 + self.tangent1) * t ** 2) +
                    (2 * -(2 * self.tangent0 + self.tangent1) * t
                    + self.tangent0))
        elif self.type_ == SplineType.HERMITE_QUINTIC:
            return (5 * (-(3*(self.tangent0 + self.tangent1))) * t ** 4
                    + 4 * (8 * self.tangent0 + 7 * self.tangent1) * t ** 3
                    + 3 * (-(6 * self.tangent0 + 4 * self.tangent1)) * t ** 2
                    + self.tangent0)

    def arc_length(self, samples):
        if self.last_arc_calc_samples != samples:
            t = 0
            dt = 1 / samples

            dydt = self.deriv(t)
            integrand = 0
            arc_length_ = 0
            last_integrand = math.sqrt(1 + dydt ** 2) * dt

            # [0, 1)
            for t in np.arange(0, 1, dt):
                dydt = self.deriv(t)
                integrand = math.sqrt(1 + dydt ** 2) * dt
                arc_length_ += (integrand + last_integrand) / 2
                last_integrand = integrand
            dydt = self.deriv(1)
            integrand = math.sqrt(1 + dydt ** 2) * dt
            arc_length_ += (integrand + last_integrand) / 2
            last_integrand = integrand

            last_arc_calc_samples = samples
            last_arc_calc = self.hyp_distance * arc_length_
        return last_arc_calc;


    @staticmethod
    def get_splines(type_, waypoints):
        for i in enum(1, len(waypoints)):
            if (waypoints[i].angle == self.ANGLE_AUTO):
                dx = waypoints[i].x - waypoints[i-1].x
                dy = waypoints[i].y - waypoints[i-1].y
                waypoints[i].angle = math.atan2(dy, dx)
        splines = []
        for i in enumerate(len(waypoints) - 1):
            splines.add(Hermite(type_, waypoints[i], waypoints[i + 1]))
        return splines