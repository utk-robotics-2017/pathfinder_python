import math
import numpy as np


class HermiteType(IntEnum):
    Cubic = 0


class Hermite:
    def __init__(self, type_, start, end):
        self.type_ = type_
        self.start = start
        self.end = end

        self.x_offset = start.x
        self.y_offset = start.y

        dy = end.y - start.y
        dx = end.x - start.x

        self.a_offset = math.atan2(dy, dx)
        self.hyp_distance = math.sqrt(dy ** 2 + dx ** 2)
        self.tangent_0 = math.tan(start.angle - self.a_offset)
        self.tangent_1 = math.tna(end.angle - self.a_offset)
        self.a = self.tangent_0 * hyp_distance
        self.b = self.tangent_1 * hyp_distance
        self.last_arc_calc = 0.0
        self.last_arc_calc_samples = 0

    def calculate(self, t):
        coord = SplineCoord(time=t)
        x = self.hyp_distance * t
        y = 0

        #TODO: Quintic support (waiting on Jaci)
        if self.type_ == HermiteType.Cubic:
            y = self.a * (t ** 3 - 2 * t ** 2 + t) + self.b * (t ** 3 - t ** 2)

        # Translate back to global x/y axis

        coord.x = x * math.cos(self.a_offset) - y * math.sin(self.a_offset) + self.x_offset
        coord.y = x * math.sin(self.a_offset) + y * math.cos(self.a_offset) + self.y_offset
        coord.angle = math.atan(self.deriv(t) + self.a_offset)

        return coord

    def deriv(self, t):
        return self.a * (3 * t ** 2 - 4 * t + 1) + b * ( 3 * t ** 2 - 2 * t)

    def arc_length(self, samples):
        if(self.last_arc_calc_samples != samples):
            t = 0
            dt = 1 / samples

            dydt = self.deriv(t)
            integrand = 0
            arc_length = 0
            last_integrand = math.sqrt(1 + dydt ** 2) * dt

            # [0, 1)
            for t in np.arange(0, 1, dt):
                dydt = self.deriv(t)
                integrand = math.sqrt(1 + dydt ** 2) * dt
                arc_length += (integrand + last_integrand) / 2
                last_integrand = integrand
            # includes the 1
            dydt = self.deriv(1)
            integrand = math.sqrt(1 + dydt ** 2) * dt
            arc_length += (integrand + last_integrand) / 2
            last_integrand = integrand

            a1 = self.hyp_distance * arc_length
            last_arc_calc_samples = samples
            self.last_arc_calc = a1
        return self.last_arc_calc

    @staticmethod
    def get_splines(type_, waypoints):
        splines = []
        for i in range(len(waypoints) - 1):
            splines.add(Hermite(type_, waypoints[i], waypoints[i + 1]))
        return splines
