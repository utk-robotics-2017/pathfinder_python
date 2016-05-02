from TrajectoryInfo import TrajectoryInfo
from TrajectoryConfig import TrajectoryConfig


class Trajectory:
    def __init__(self):
        self.spline_list = []
        self.length_list = []
        self.total_length = 0.0
        self.length = 0
        self.path_length = 0
        self.info = None
        self.config = None
