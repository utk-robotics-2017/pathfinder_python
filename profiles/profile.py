from enum import IntEnum
from ..util.units import Distance
from ..util.decorators import attr_check, type_check
from ..structs.segment import Segment


class ProfileType(IntEnum):
	TRAPEZOIDAL = 0


class Status(IntEnum):
	DONE = 0
	DECEL = 1
	ACCEL = 2
	LEVEL = 3


@attr_check
class Profile:
    setpoint = Distance
    tolerance = Distance

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
        raise NotImplementedError("Profile calculate")
