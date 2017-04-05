from enum import IntEnum


class Status(IntEnum):
    ACCEL = 0
    DECEL = 1
    LEVEL = 2
    DONE = 3


class Profile:
    def calculate(self, time, last_segment):
        raise NotImplementedError("Profile calculate hasn't been implemented")
