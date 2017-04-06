from enum import IntEnum


class ProfileType(IntEnum):
	TRAPEZOIDAL = 0


class Status(IntEnum):
	DONE = 0
	DECEL = 1
	ACCEL = 2
	LEVEL = 3


class Profile:
    def calculate(self, t, previous_segment=None):
        raise NotImplementedError("Profile calcualte")
