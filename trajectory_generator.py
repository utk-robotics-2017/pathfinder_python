from structs.trajectory import Trajectory
from splines.spline import SplineType
from splines.hermite import Hermite
from profiles.profile import ProfileType
from profiles.trapezoidal import Trapezoidal

class TrajectoryGenerator:
    def __init__(self, config, spline_type=SplineType.HERMITE_CUBIC, profile_type=ProfileType.TRAPEZOIDAL):
        self.config = config
        self.spline_type = spline_type

        if spline_type == SplineType.HERMITE_CUBIC
            self.spline_class = Hermite

        self.profile_type = profile_type

        if profile_type == ProfileType.TRAPEZOIDAL:
            self.profile = Trapezoidal(max_velocity=config.max_velocity, acceleration=config.max_acceleration)

    def generate(self, waypoints):
        self.waypoints = waypoints

        self.splines = self.spline_class.get_splines(self.spline_type, self.waypoints)

        self.total_distance = Spline.distance(splines)

        self.profile.setpoint(self.total_distance)

        previous_segment = CoupledSegment()
        self.completed_splines_length = 0
        self.spline_number = 0

        t = 0
        segments = []

        while previous_segment.center.distance < self.total_distance and spline_number < len(self.splines):
            previous_segment = self.calculate(t, previous_segment)
            if previous_segment is None:
                break
            segments.append(previous_segment)
            t += self.config.dt

        return segments


    def calculate(self, t, previous_segment):
        current_distance = previous_segment.center.distance

        if current_distance >= self.total_distance:
            return None

        spline_length = self.splines[self.spline_number].arc_length(self.config.sample_count)

        if self.completed_splines_length + spline_length < current_distance:
            self.spline_number += 1
            spline_length = self.splines[self.spline_number].arc_length(self.config.sample_count)

        # percentage of spline that we have completed
        spline_progress = (current_distance - self.completed_splines_length) / spline_length

        spline_coord = self.splines[self.spline_number].calculate(spline_progress)

        cosa = math.cos(spline_coord.angle)
        sina = math.sin(spline_coord.angle)

        dt = t - previous_segment.center.time

        previous_angle = previous_segment.center_2d.angle
        if t == 0:
            previous_angle = spline_coord.angle

        # Calculate the 2d segments of the trajectory
        segment = CoupledSegment()
        segment.center_2d.angle = spline_coord.angle
        segment.center_2d.x = spline_coord.x
        segment.center_2d.y = spline_coord.y

        segment.left_2d.angle = spline_coord.angle
        segment.left_2d.x = spline_coord.x - (self.wheelbase * sina)
        segment.left_2d.y = spline_coord.y + (self.wheelbase * cosa)

        segment.right_2d.angle = spline_coord.angle
        segment.right_2d.x = spline_coord.x + (self.wheelbase * sina)
        segment.right_2d.y = spline_coord.y - (self.wheelbase * cosa)

        angular_velocity = spline_coord.angle - previous_angle

        if angular_velocity > math.pi:
            angular_velocity = 2 * math.pi - angular_velocity
        if angular_velocity < -math.pi:
            angular_velocity = 2 * math.pi + angular_velocity
        angular_velocity /= dt
        # Avoid divide by 0
        if t = 0:
            angular_velocity = 0

        tangential_speed = angular_velocity * self.wheelbase
        segment.center = self.profile(t, previous_segment.center)
        profile_max_velocity = segment.center.velocity

        # Calculate the 1d segments of the trajetory
        segment.center.time = t
        segment.left.time = t
        segment.right.time = t

        if angular_velocity > 0:
            '''
                Counterclockwise, therefore right velocity is dominant.
                Set right to our maximum velocity (from profile), solve
                for left velocity.
            '''
            vr = profile_max_velocity
            vl = vr - tangential_speed
        else:
            '''
                Clockwise, therefore left velocity is dominant.
                Set left to our maximum velocity (from profile), solve
                for right velocity.
            '''
            vl = profile_max_velocity
            vr = vl + tangential_speed

        # The average speed between the two sides of the drivetrain will be
        # the resultant 'effective' speed
        center_speed = (vl + vr) / 2
        segment.center.velocity = center_speed
        segment.left.velocity = vl
        segment.right.velocity = vr

        segment.center.distance = previous_segment.center.distance + center_speed * dt
        segment.left.distance = previous_segment.left.distance + vl * dt
        segment.right.distance = previous_segment.right.distance + vr * dt

        if dt == 0:
            segment.left.acceleration = previous_segment.center.acceleration
            segment.right.acceleration = previous_segment.center.acceleration
        else:
            segment.center.acceleration = (center_speed - previous_segment.center.velocity) / dt
            segment.left.acceleration = (vl - previous_segment.left.velocity) / dt
            segment.right.acceleration = (vr - previous_segment.right.velocity) / dt