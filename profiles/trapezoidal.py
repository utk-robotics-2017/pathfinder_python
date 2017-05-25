from .profile import Profile, Status
from util.decorators import attr_check, type_check, void
from util.units import Distance, Velocity, Acceleration, Time
from structs.segment import Segment


@attr_check
class Trapezoidal(Profile):
    ''' A type of motion profile based on a trapezoid

        Attributes
        ----------
        max_velocity : Velocity
            The maximum velocity of the robot

        acceleration : Acceleration

        tolerance : Distance
            The amount of leeway for reaching the setpoint

        distance_integral : Distance
            Used for the Scurve.
    '''
    max_velocity = Velocity
    acceleration = Acceleration
    distance_integral = Distance

    @type_check
    def __init__(self, max_velocity: Velocity, acceleration: Acceleration, tolerance: Distance=Distance(0.05, Distance.inch), timescale: Time=Time(0.001, Time.s)):
        self.max_velocity = max_velocity
        self.acceleration = acceleration
        self.tolerance = tolerance
        self.timescale = timescale

    @type_check
    def calculate_single(self, t: Time, previous_segment: (void, Segment)=None):
        ''' Calculates the next segment based on the previous one

            Parameters
            ----------
            t : Time
                The start time for the next segment
            previous_segment : Segment
                The previous segment in the path

            Returns
            -------
            Status
                The status of the motion profile
            Segment
                The next segment in the path
        '''
        if previous_segment is None:
            previous_segment = Segment(distance=0, velocity=0, acceleration=0, time=0)

        segment = Segment(time=t)

        dt = t - previous_segment.time

        if abs(self.setpoint - previous_segment.distance) <= self.tolerance:
            segment.distance = previous_segment.distance
            return Status.DONE, segment

        accel = 0
        if previous_segment.distance < self.setpoint:
            accel = self.acceleration
        else:
            accel = -self.acceleration

        decel_time = previous_segment.velocity / accel
        decel_distance = previous_segment.velocity * decel_time - 0.5 * accel * decel_time ** 2

        decel_error = previous_segment.distance + decel_distance - self.setpoint

        sixth = 1 / 6

        # Deceleration zone
        if(abs(decel_error) <= self.tolerance or
           (self.setpoint < 0 and decel_error < self.tolerance) or
           (self.setpoint > 0 and decel_error > self.tolerance)):
            segment.acceleration = -accel
            segment.velocity = previous_segment.velocity - (accel * dt)
            segment.distance = previous_segment.distance + (previous_segment.velocity * dt) - (0.5 * accel * dt ** 2)
            self.distance_integral += previous_segment.distance * dt + (0.5 * previous_segment.velocity * dt ** 2) + (sixth * (-accel) * dt ** 3)
            return Status.DECEL, segment

        # Acceleration zone
        elif (abs(previous_segment.velocity) < self.max_velocity):
            segment.acceleration = accel
            v = previous_segment.velocity + (accel * dt)
            segment.velocity = -self.max_velocity if v < -self.max_velocity else (self.max_velocity if v > self.max_velocity else v)
            segment.distance = previous_segment.distance + (previous_segment.velocity * dt) + (0.5 * accel * dt ** 2)
            self.distance_integral += previous_segment.distance * dt + (0.5 * previous_segment.velocity * dt ** 2) + (sixth * accel * dt ** 3)
            return Status.ACCEL, segment

        # Level
        segment.acceleration = 0
        segment.velocity = previous_segment.velocity
        segment.distance = previous_segment.distance + previous_segment.velocity * dt
        self.distance_integral += previous_segment.distance * dt + (0.5 * previous_segment.velocity * dt ** 2)
        return Status.LEVEL, segment
