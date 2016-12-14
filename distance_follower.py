class DistanceFollower:
    def __init__(self, trajectory):
        self.last_error = 0.0
        self.heading = 0.0
        self.output = 0.0
        self.segment = 0
        self.kp = 0.0
        self.ki = 0.0
        self.kd = 0.0
        self.kv = 0.0
        self.ka = 0.0
        self.trajectory = trajectory

    def configurePIDVA(self, kp, ki, kd, kv, ka):
        '''
            Configure the PID/VA Variables for the Follower
            :param kp The proportional term. This is usually quite high (0.8 - 1.0 are common values)
            :param ki The integral term. Currently unused.
            :param kd The derivative term.
                Adjust this if you are unhappy with the tracking of the follower. 0.0 is the default
            :param kv The velocity ratio. This should be 1 over your maximum velocity @ 100% throttle.
                    This converts m/s given by the algorithm to a scale of -1..1 to be used by your
                    motor controllers
            :param ka The acceleration term.
                Adjust this if you want to reach higher or lower speeds faster. 0.0 is the default
        '''
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.kv = kv
        self.ka = ka

    def calculate(self, distance):
        if(self.segment < len(self.trajectory)):
            seg = self.trajectory[self.segment]
            error = seg.position - distance
            calculated_value = (self.kp * error + self.kd * ((error - self.last_error) / seg.dt) +
                                (self.kv * seg.velocity + self.ka * seg.acceleration))
            self.last_error = error
            self.heading = seg.heading
            self.segment = self.segment + 1
            return calculated_value
        else:
            return 0.0

    def setTrajectory(self, trajectory):
        '''
            Set a new trajectory to follow, and reset the cumulative errors and segment counts
        '''
        self.trajectory = trajectory
        self.reset()

    def reset(self):
        '''
            Reset the follower to start again. Encoders must be reconfigured.
        '''
        self.segment = 0
        self.last_error = 0

    def isFinished(self):
        '''
            :return whether we have finished tracking this trajectory or not.
        '''
        return self.segment >= len(self.trajectory)
