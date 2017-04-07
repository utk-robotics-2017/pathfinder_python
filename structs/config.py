class Config:
    def __init__(self, **kwargs):
        self.dt = 0.0
        self.max_velocity = 0.0
        self.max_acceleration = 0.0
        self.max_jerk = 0.0
        self.sample_count = 0

        self.__dict__.update(kwargs)
