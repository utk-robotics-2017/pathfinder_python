from .TrajectoryInfo import TrajectoryInfo
from .TrajectoryConfig import TrajectoryConfig


class Trajectory:
    spline_list = []
    length_list = []
    total_length = 0.0
    length = 0
    path_length = 0
    info = None
    config = None
