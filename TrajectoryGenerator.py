from Structs.Trajectory import Trajectory
from SplineGenerator import SplineGenerator
from SplineGenerator import FitType
from TrajectoryPlanner import TrajectoryPlanner
from SplineUtils import SplineUtils


class TrajectoryGenerator:
    def __init__(self, path, config):
        self.path = path
        self.config = config
        self.splineGenerator3 = SplineGenerator(FitType.CUBIC)
        self.splineGenerator5 = SplineGenerator(FitType.QUINTIC)
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
            s3 = self.splineGenerator3.fit(self.path[i], self.path[i + 1])
            dist3 = self.splineUtils.get_arc_length(s3, self.config.sample_count)
            
            s3_rev = self.splineGenerator3.fit(self.path[i + 1], self.path[i])
            dist3_rev = self.splineUtils.get_arc_length(s3_rev, self.config.sample_count)

            s5 = self.splineGenerator5.fit(self.path[i], self.path[i + 1])
            dist5 = self.splineUtils.get_arc_length(s5, self.config.sample_count)

            s5_rev = self.splineGenerator5.fit(self.path[i + 1], self.path[i])
            dist5_rev = self.splineUtils.get_arc_length(s5_rev, self.config.sample_count)

            min_dist = min(dist3, dist3_rev, dist5, dist5_rev)
            
            if min_dist == dist3:
                s = s3
                dist = dist3
            elif min_dist == dist3_rev:
                s = s3_rev
                dist = dist3_rev
            elif min_dist == dist5:
                s = s5
                dist = dist5
            else:
                s = s5_rev
                dist = dist5_rev
            
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
