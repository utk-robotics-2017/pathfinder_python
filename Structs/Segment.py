class Segment:
    def __init__(self, dt, x, y, position, velocity, acceleration, jerk, heading):
        self.dt = dt
        self.x = x
        self.y = y
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.jerk = jerk
        self.heading = heading