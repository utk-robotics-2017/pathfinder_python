from .profile import Profile, Status


class Trapezoidal(Profile):
    def __init__(self, setpoint, max_velocity, acceleration):
        self.setpoint = setpoint
        self.max_velocity = max_velocity
        self.acceleration = acceleration

    def calculate(self, t, previous_segment=None):
        if previous_segment is None:
            previous_segment = Segment(distance=0, velocity=0, acceleration=0, time=0)

        segment = Segment(time=t)

        decel_time = previous_segment.velocity / self.acceleration
        decel_distance = previous_segment.velocity * decel_time - 0.5 * self.acceleration * decel_time ** 2

        dt = t - previous_segment.time

        if previous_segment.distance >= self.setpoint:
            segment.distance = previous_segment.distance
            return Status.DONE, segment

        # Deceleration zone
        if previous_segment.distance + decel_distance >= self.setpoint:
            segment.acceleration = -self.acceleration
            segment.velocity = previous_segment.velocity - self.acceleration * dt
            segment.distance = previous_segment.distance + previous_segment.velocity * dt - (0.5 * self.acceleration * dt ** 2)
            return Status.DECEL, segment

        # Acceleration zone
        if previous_segment.velocity < self.max_velocity:
            segment.acceleration = self.acceleration
            segment.velocity = min(previous_segment.velocity + self.acceleration * dt, self.max_velocity)
            segment.distance = previous_segment.distance + previous_segment.velocity * dt + 0.5 * self.acceleration * dt ** 2
            return Status.ACCEL, segment

        # Level
        segment.acceleration = 0
        segment.velocity = previous_segment.velocity
        segment.distance = previous_segment.distance + previous_segment.velocity * dt
        return Status.LEVEL, segment
