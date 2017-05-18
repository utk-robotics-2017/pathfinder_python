from enum import IntEnum
from util.units import Distance, Time
from util.decorators import attr_check, type_check, void
from structs.segment import Segment


class ProfileType(IntEnum):
    ''' An enumeration of the motion profile types.
    '''
    TRAPEZOIDAL = 0


class Status(IntEnum):
    ''' An enumeration of the motion profile statuses.
    '''
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
    def calculate(self, t: Time, previous_segment: (void, Segment)=None):
        ''' Calculates the next segment based on the values from the previous one

            Note
            ----
            Effectively a virtual function which must be overwritten by a child
        '''
        raise NotImplementedError("Profile calculate")
