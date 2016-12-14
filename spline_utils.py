import math
from structs.coord import Coord
from mathutil import bound_radians


class SplineUtils:
    def get_coords(self, s, percentage):
        percentage = max(min(percentage, 1), 0)
        x = percentage * s.knot_distance
        y = (s.a * x + s.b) * (x * x * x * x) + (s.c * x + s.d) * (x * x) + s.e * x

        cos_theta = math.cos(s.angle_offset)
        sin_theta = math.sin(s.angle_offset)

        c = Coord(x * cos_theta - y * sin_theta + s.x_offset, x * sin_theta + y * cos_theta + s.y_offset)
        return c

    def get_deriv(self, s, percentage):
        x = percentage * s.knot_distance
        return (5 * s.a * x + 4 * s.b) * (x * x * x) + (3 * s.c * x + 2 * s.d) * x + s.e

    def get_deriv_2(self, a, b, c, d, e, k, p):
        x = p * k
        return (5 * a * x + 4 * b) * (x * x * x) + (3 * c * x + 2 * d) * x + e

    def get_angle(self, s, percentage):
        return bound_radians(math.atan(self.get_deriv(s, percentage)) + s.angle_offset)

    def get_arc_length(self, s, sample_count):
        sample_count_d = float(sample_count)
        a = s.a
        b = s.b
        c = s.c
        d = s.d
        e = s.e
        knot = s.knot_distance

        arc_length = 0.0
        t = 0.0
        dydt = 0.0

        deriv0 = self.get_deriv_2(a, b, c, d, e, knot, 0)

        integrand = 0.0
        last_integrand = math.sqrt(1 + deriv0 * deriv0) / sample_count_d

        for i in range(sample_count + 1):
            t = i / sample_count_d
            dydt = self.get_deriv_2(a, b, c, d, e, knot, t)
            integrand = math.sqrt(1 + dydt * dydt) / sample_count_d
            arc_length = arc_length + (integrand + last_integrand) / 2
            last_integrand = integrand
        al = knot * arc_length
        s.arc_length = al
        return al

    def get_progress_for_distance(self, s, distance, sample_count):
        sample_count_d = float(sample_count)

        a = s.a
        b = s.b
        c = s.c
        d = s.d
        e = s.e
        knot = s.knot_distance

        arc_length = 0.0
        t = 0.0
        dydt = 0.0
        last_arc_length = 0.0

        deriv0 = self.get_deriv_2(a, b, c, d, e, knot, 0)

        integrand = 0
        last_integrand = math.sqrt(1 + deriv0 * deriv0) / sample_count_d

        distance = distance / knot

        for i in range(sample_count + 1):
            t = i / sample_count_d
            dydt = self.get_deriv_2(a, b, c, d, e, knot, t)
            integrand = math.sqrt(1 + dydt * dydt) / sample_count_d
            arc_length = arc_length + (integrand + last_integrand) / 2
            if arc_length > distance:
                break
            last_integrand = integrand
            last_arc_length = arc_length

        interpolated = t
        if arc_length != last_arc_length:
            interpolated = interpolated + ((distance - last_arc_length) /
                                           (arc_length - last_arc_length) - 1) / sample_count_d
        return interpolated
