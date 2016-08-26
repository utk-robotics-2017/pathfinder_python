from Structs.Trajectory import Trajectory
from SplineGenerator import SplineGenerator
from SplineGenerator import FitType
from TrajectoryPlanner import TrajectoryPlanner
from SplineUtils import SplineUtils


class TrajectoryGenerator:
    def __init__(self, path, config, fit_type=FitType.CUBIC):
        self.path = path
        self.config = config
        self.splineGenerator = SplineGenerator(fit_type)
        self.trajectory = Trajectory()
        self.splineUtils = SplineUtils()
        self.planner = TrajectoryPlanner(config)
        self.prepare()

    def prepare(self):
        if(len(self.path) < 2):
            print "Error: TrajectoryGenerator preparation failed: path length is less than 2"
            return

        self.trajectory.spline_list = []
        self.trajectory.length_list = []

        self.trajectory.total_length = 0
        for i in range(len(self.path) - 1):
            s = self.splineGenerator.fit(self.path[i], self.path[i + 1])
            dist = self.splineUtils.get_arc_length(s, self.config.sample_count)
            self.trajectory.spline_list.append(s)
            self.trajectory.length_list.append(dist)
            self.trajectory.total_length = self.trajectory.total_length + dist

        self.config.dest_pos = self.trajectory.total_length
        self.config.src_theta = self.path[0].angle
        self.config.dest_theta = self.path[0].angle

        self.planner.prepare()

        self.trajectory.length = self.planner.info.length
        self.trajectory.path_length = len(self.path)
        self.trajectory.config = self.config

    def generate(self):
        trajectory_length = self.trajectory.length
        path_length = self.trajectory.path_length

        splines = self.trajectory.spline_list

        spline_lengths = self.trajectory.length_list

        segments = self.planner.create()

        spline_i = 0
        spline_pos_initial = 0.0

        for i in range(trajectory_length):
            displacement = segments[i].displacement

            while True:
                pos_relative = displacement - spline_pos_initial
                # all but the last point on a spline
                if(pos_relative <= spline_lengths[spline_i]):
                    si = splines[spline_i]
                    percentage = self.splineUtils.get_progress_for_distance(si, pos_relative, self.config.sample_count)
                    coords = self.splineUtils.get_coords(si, percentage)
                    segments[i].heading = self.splineUtils.get_angle(si, percentage)
                    segments[i].x = coords.x
                    segments[i].y = coords.y
                    break
                # finish a spline
                elif spline_i < path_length - 2:
                    spline_pos_initial += spline_lengths[spline_i]
                    spline_i += 1
                # Very last point
                else:
                    si = splines[path_length - 2]
                    segments[i].heading = self.splineUtils.get_angle(si, 1.0)
                    coords = self.splineUtils.get_coords(si, 1.0)
                    segments[i].x = coords.x
                    segments[i].y = coords.y
                    break

        splines = []
        spline_lengths = []

        return segments
