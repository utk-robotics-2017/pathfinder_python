class TrajectoryConfig:
    def __init__(self):
        self.dt = 0.0
        self.max_v = 0.0
        self.max_a = 0.0
        self.max_j = 0.0
        self.src_v = 0.0
        self.src_theta = 0.0
        self.dest_pos = 0.0
        self.dest_v = 0.0
        self.dest_theta = 0.0
        self.sample_count = 0

    def toString(self):
        return "dt: %f max_v: %f max_a: %f max_j: %f src_v: %f src_theta: %f dest_pos: %f dest_v: %f dest_theta: %f sample_count: %f" % (self.dt, self.max_v, self.max_a, self.max_j, self.src_v, self.src_theta, self.dest_pos, self.dest_v, self.dest_theta, self.sample_count)
