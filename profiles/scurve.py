import math
from .profile import Profile, Status
from ..utils.decorators import attr_check, type_check, void
from ..utils.units import Distance, Velocity, Acceleration, Jerk, Time, zero_unit
from ..structs.segment import Segment
from .trapezoidal import Trapezoidal


@attr_check
class Scurve(Profile):
    max_velocity = Velocity
    max_acceleration = Acceleration
    jerk = Jerk
    tolerance = Distance
    jerk_out = Jerk
    velocity_profile = Trapezoidal

    @type_check
    def __init__(self, max_velocity: Velocity,
                 acceleration: Acceleration,
                 jerk: Jerk,
                 tolerance: Distance=Distance(0.05, Distance.inch),
                 timescale: Time=Time(0.001, Time.s)):
        self.max_velocity = max_velocity
        self.max_acceleration = acceleration
        self.jerk = jerk
        self.tolerance = tolerance
        self.timescale = timescale

        self.velocity_profile = Trapezoidal(acceleration, jerk, tolerance, timescale)
        self.velocity_profile.set_setpoint(max_velocity)

    def calculate_single(self, t: Time, previous_segment: (void, Segment)=None):
        velocity_segment_in = Segment(time=previous_segment.time,
                                      distance=Distance(previous_segment.velocity.base_value),
                                      velocity=Velocity(previous_segment.acceleration.base_value))

        velocity_segment = Segment()
        segment = Segment(time=t)

        dt = t - previous_segment.time

        if abs(previous_segment.distance - self.setpoint) < self.tolerance:
            self.jerk_out = zero_unit
            segment.distance = previous_segment.distance
            return Status.DONE, segment

        jerk = zero_unit
        if previous_segment.distance < self.setpoint:
            # Below setpoint
            jerk = self.jerk
        else:
            # Above setpoint
            jerk = -self.jerk

        vpstatus = 0
        max_acceleration = self.max_acceleration if self.setpoint > 0 else -self.max_acceleration
        triangle_peak_time = math.sqrt(2 * (previous_segment.velocity / 2) / jerk)
        saturation_time = (-max_acceleration - previous_segment.acceleration) / (-jerk)

        dejerk_dist = previous_segment.velocity * triangle_peak_time
        if abs(saturation_time) < abs(triangle_peak_time):
            t0 = (-self.max_acceleration - previous_segment.acceleration) / (-jerk)
            t2 = self.max_acceleration / jerk

            a0 = previous_segment.acceleration
            v0 = previous_segment.velocity

            sixth = 1 / 6

            v1 = v0 + a0 * t0 + 0.5 * (-jerk) * t0 ** 2
            v2 = self.max_acceleration.base_value * t2 + 0.5 * (-jerk) * t2 ** 2

            if v1 < v2:
                t0 = zero_unit

            t1 = (v1 - v2) / self.max_acceleration

            if t1 < 0:
                t2 = t2 + t1
                t1 = zero_unit

            s0 = v0 * t0 + 0.5 * a0 * t0 ** 2 + sixth * (-jerk) * t0 ** 3
            s1 = v1 * t1 + 0.5 * (-self.max_acceleration) * t1 ** 2
            s2 = v2 * t2 + 0.5 * (-self.max_acceleration) * t2 ** 2 + sixth * jerk * t2 ** 3

            dejerk_dist = s0 + s1 + s2

        dejerk_error = previous_segment.distance + dejerk_dist - self.setpoint

        # TODO: Unfortunately we can't use trapezoidal profiles for the velocity profile.
        # This is because we can't integrate the velocity the way we normally would, making it very
        # difficult to accurately generate a path.

        if(abs(dejerk_error) <= self.tolerance or
           (self.setpoint < 0 and dejerk_error < -self.tolerance) or
           (self.setpoint > 0 and dejerk_error > self.tolerance)):
            self.velocity_profile.distance_integral = previous_segment.distance
            self.velocity_profile.set_setpoint(0)
            vpstatus, velocity_segment = self.velocity_profile.calculate(t, velocity_segment_in)

            self.jerk_out = velocity_segment.acceleration
            segment.acceleration = velocity_segment.velocity
            segment.velocity = velocity_segment.distance
            segment.distance = velocity_segment.distance_integral
            return Status.DECEL, segment
        elif abs(previous_segment.velocity) < self.max_velocity - self.tolerance:
            self.velocity_profile.distance_integral = previous_segment.distance
            self.velocity_profile.setpoint(-self.max_velocity if self.setpoint < 0 else self.max_velocity)
            vpstatus, velocity_segment = self.velocity_profile.calculate(t, velocity_segment_in)

            self.jerk_out = velocity_segment.acceleration
            segment.acceleration = velocity_segment.velocity
            segment.velocity = velocity_segment.distance
            segment.distance = self.velocity_profile.distance_integral
            return Status.ACCEL, segment

        # If nothing else, we have leveled out, hold steady velocity
        self.jerk_out = zero_unit
        segment.acceleration = zero_unit
        segment.velocity = previous_segment.velocity
        segment.distance = previous_segment.distance + (previous_segment.velocity * dt)
        return Status.LEVEL, segment
