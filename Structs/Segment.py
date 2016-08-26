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

    def toString(self):
        print "dt: %f x: %f y: %f d: %f v: %f a: %f j: %f h: %f" % (self.dt, self.x,
        self.y, self.displacement, self.velocity, self.acceleration, self.jerk, self.heading)
