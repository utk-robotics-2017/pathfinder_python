from structs.trajectory import Trajectory
from splines.spline import SplineType
from splines.hermite import Hermite
from profiles.profile import ProfileType
from profiles.trapezoidal import Trapezoidal

class TrajectoryGenerator:
    def __init__(self, waypoints, config, spline_type=SplineType.HERMITE_CUBIC, profile_type=ProfileType.TRAPEZOIDAL):
        self.waypoints = waypoints
        self.config = config
        self.spline_type = spline_type

        if spline_type == SplineType.HERMITE_CUBIC
            self.spline_class = Hermite

        self.profile_type = profile_type

        if profile_type == ProfileType.TRAPEZOIDAL:
            self.profile_class = Trapezoidal

    def generate(self):
        splines = self.spline_class.get_splines(self.spline_type, self.waypoints)


