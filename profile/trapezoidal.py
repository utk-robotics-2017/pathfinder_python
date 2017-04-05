from .profile import Status, Profile


class Trapezoidal(Profile):
    def __init__(self, setpoint, max_velocity, acceleration):
        self.setpoint = setpoint
        self.max_velocity = max_velocity
        self.acceleration = acceleration

    def calculate(self, time, last_segment=None):
        segment = Segment(time=time)

        if last_segment is None:
            last_segment = Segment(distance=0, velocity=0, acceleration=0, time=0)

        # t = v/a
        decel_time = last_segment.velocity / self.acceleration

        # d = vt + 0.5at^2
        decel_distance = last_segment.velocity * decel_time - 0.5 * self.acceleration * decel_time ** 2

        dt = time - last_segment.time

        if(last_segment.distance >= self.setpoint):
            # drop all to 0 and return
            segment.distance = last_segment.distance
            return Status.DONE, segment

        if last_segment.distance + decel_distance >= self.setpoint:
            # If we start decelerating now, we will hit the setpoint
            segment.acceleration = -self.acceleration
            segment.velocity = last_segment.velocity - (self.acceleration * dt)
            segment.distance = last_segment.distance + (last_segment.velocity * dt) - (0.5 * self.acceleration * dt ** 2)
            return Status.DECEL, segment

        if last_segment.velocity < self.max_velocity:
            # We are in the speed up portion of the profile
            segment.acceleration = self.acceleration
            segment.velocity = math.min(last_segment.velocity + (self.acceleration * dt), self.max_velocity)
            segment.distance = last_segment.distance + (last_segment.velocity * dt) + (0.5 * self.acceleration * dt ** 2)
            return Status.ACCEL, segment

        # Hold steady velocity
        segment.acceleration = 0
        segment.velocity = last_segment.velocity
        segment.distance = last_segment.distance + last_segment.velocity * dt
        return Status.LEVEL, segment
