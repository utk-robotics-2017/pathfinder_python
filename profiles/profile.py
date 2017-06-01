from enum import IntEnum
from utils.units import Distance, Time
from utils.decorators import attr_check, type_check, void
from structs.segment import Segment


class ProfileType(IntEnum):
    ''' An enumeration of the motion profile types. '''
    TRAPEZOIDAL = 0
    SCURVE = 1


class Status(IntEnum):
    ''' An enumeration of the motion profile statuses. '''
    DONE = 0
    DECEL = 1
    ACCEL = 2
    LEVEL = 3


@attr_check
class Profile:
    ''' The base class for the motion profiles

        Attributes
        ----------
        setpoint : Distance
            The desired distance to travel
        tolerance : Distance
            The amount of precision in which to meet the setpoint
    '''
    setpoint = Distance
    tolerance = Distance
    timescale = Time

    # TODO: create properties
    @type_check
    def set_setpoint(self, setpoint: Distance) -> void:
        self.setpoint = setpoint

    @type_check
    def get_setpoint(self) -> Distance:
        return self.setpoint

    @type_check
    def set_tolerance(self, tolerance: Distance) -> void:
        self.tolerance = tolerance

    @type_check
    def get_tolerance(self) -> Distance:
        return self.tolerance

    @type_check
    def set_timescale(self, timescale: Time) -> void:
        self.timescale = timescale

    @type_check
    def get_timescale(self) -> Time:
        return self.timescale

    @type_check
    def calculate_single(self, t: Time, previous_segment: (void, Segment)=None):
        ''' Calculates the next segment based on the values from the previous one

            Note
            ----
            Effectively a virtual function which must be overwritten by a child
        '''
        raise NotImplementedError("Profile calculate")

    @type_check
    def calculate(self, t: Time, previous_segment: (void, Segment)=None):
        ''' Calculates the next segment based on the previous one

            Parameters
            ----------
            t : Time
                The start time for the next segment
            previous_segment : Segment
                The previous segment in the path

            Returns
            -------
            Status
                The status of the motion profile
            Segment
                The next segment in the path
        '''
        temp = Segment(time=previous_segment.time,
                       distance=previous_segment.distance,
                       velocity=previous_segment.velocity,
                       acceleration=previous_segment.acceleration)

        dt = t - previous_segment.time

        slice_count = int(dt.base_value / self.timescale.base_value)

        # The time difference provided is smaller than the target timescale,
        # use the smaller of the two.
        if(slice_count < 1):
            return self.calculate_single(t, previous_segment)
        else:
            for i in range(slice_count):
                time_slice = temp.time + self.timescale
                status, temp = self.calculate_single(time_slice, temp)
                if status == Status.DONE:
                    break
        return temp
