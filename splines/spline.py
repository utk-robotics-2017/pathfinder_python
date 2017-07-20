from enum import IntEnum
from ..util.units import Distance, Time
from ..utils.decorators import type_check


class SplineType(IntEnum):
    HERMITE_CUBIC = 0
    HERMITE_QUINTIC = 1


class Spline:
    @type_check
    def calculate(self, t: Time):
        raise NotImplementedError("Spline calculate")

    @type_check
    def derive(self, t: Time):
        raise NotImplementedError("Spline derive")

    @type_check
    def arc_length(self, samples: list):
        raise NotImplementedError("Spline arc_length")

    @staticmethod
    @type_check
    def get_splines():
        raise NotImplementedError("Spline get_splines")

    @staticmethod
    @type_check
    def distance(splines: list, samples: list) -> Distance:
        dist = Distance(0)
        for spline in splines:
            dist += spline.arc_length(samples)
        return dist
