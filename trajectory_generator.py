import math
from structs.config import Config
from structs.coupled_segment import CoupledSegment
from splines.spline import Spline, SplineType
from splines.hermite import Hermite
from profiles.profile import Profile, ProfileType
from profiles.trapezoidal import Trapezoidal
from utils.decorators import attr_check, type_check  # , singleton
from utils.units import Distance, Time


@attr_check
class TrajectoryGenerator:
    ''' Generates the trajectory from the given config and waypoints

        Attributes
        ----------
        config: TrajectoryConfig
            Configuration containing robot dynamics
        spline_type: int, SplineType
            Enumeration representing the type of spline to be used
        spline_class: class that is a child of Spline
            Spline class that is used to generate the splines
        profile_type: int, ProfileType
            Enumeration representing the type of motion profile to be used
        profile: Profile
            Motion Profile generator
    '''
    config = Config
    spline_type = (int, SplineType)
    # TODO: determine is class is a type for spline_class
    profile_type = (int, ProfileType)
    profile = Profile
    waypoints = list
    splines = list
    total_distance = Distance
    completed_splines_length = int
    spline_number = int

    @type_check
    def __init__(self, config: Config, spline_type: (int, SplineType)=SplineType.HERMITE_CUBIC,
                 profile_type: (int, ProfileType)=ProfileType.TRAPEZOIDAL):
        ''' Constructor

            Parameters
            ----------
            config: TrajectoryConfig
                Configuration containing robot dynamics
            spline_type: int, SplineType
                Enumeration representing the type of spline to be used
            profile_type: int, ProfileType
                Enumeration representing the type of motion profile to be used
        '''
        self.config = config
        self.spline_type = spline_type

        if spline_type in [SplineType.HERMITE_CUBIC, SplineType.HERMITE_QUINTIC]:
            self.spline_class = Hermite

        self.profile_type = profile_type

        if profile_type == ProfileType.TRAPEZOIDAL:
            self.profile = Trapezoidal(max_velocity=config.max_velocity, acceleration=config.max_acceleration)

    @type_check
    def generate(self, waypoints: list) -> list:
        ''' Generates a list of segments from the waypoints

            Parameters
            ----------
            waypoints: list(Waypoint)
                list of Waypoint structs

            Returns
            -------
            list(CoupledSegment)
                A list of the segments (center, left, and right) in terms of coupled to the 2d locations for them
        '''
        self.waypoints = waypoints

        self.splines = self.spline_class.get_splines(self.spline_type, self.waypoints)

        self.total_distance = Spline.distance(self.splines)

        self.profile.setpoint(self.total_distance)

        previous_segment = CoupledSegment()
        self.completed_splines_length = 0
        self.spline_number = 0

        t = 0
        segments = []

        while previous_segment.center.distance < self.total_distance and self.spline_number < len(self.splines):
            previous_segment = self.calculate(t, previous_segment)
            if previous_segment is None:
                break
            segments.append(previous_segment)
            t += self.config.dt

        return segments

    @type_check
    def calculate(self, t: Time, previous_segment: CoupledSegment) -> CoupledSegment:
        ''' Creates the next CoupledSegment on the path to the next waypoint from the current one

            Parameters
            ----------
            t: Time
                Current timestamp for the next CoupledSegment

            previous_segment: CoupledSegment
                The previous calculated CoupledSegment used to determine where the next
                one starts.

            Returns
            -------
            CoupledSegment
                The next CoupledSegment on the path
        '''
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

        # Calculate the 2D segments of the trajectory
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
        if t == 0:
            angular_velocity = 0

        tangential_speed = angular_velocity * self.wheelbase
        segment.center = self.profile(t, previous_segment.center)
        profile_max_velocity = segment.center.velocity

        # Calculate the 1D segments of the trajectory
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

        return segment
