class Segment:
    def __init__(self, dt, x, y, displacement, velocity, acceleration, jerk, heading):
        self.dt = dt
        self.x = x
        self.y = y
        self.displacement = displacement
        self.velocity = velocity
        self.acceleration = acceleration
        self.jerk = jerk
        self.heading = heading
