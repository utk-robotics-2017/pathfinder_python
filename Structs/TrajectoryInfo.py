class TrajectoryInfo:
    def __init__(self, filter1, filter2, length, dt, u, v, impulse):
        self.filter1 = filter1
        self.filter2 = filter2
        self.length = length
        self.dt = dt
        self.u = u
        self.v = v
        self.impulse = impulse
