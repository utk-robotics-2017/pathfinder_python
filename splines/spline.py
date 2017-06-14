from enum import IntEnum


class SplineType(IntEnum):
    HERMITE_CUBIC = 0
    HERMITE_QUINTIC = 1


class Spline:
    def calculate(self, t):
        raise NotImplementedError("Spline calculate")

    def derive(self, t):
        raise NotImplementedError("Spline derive")

    def arc_length(self, samples):
        raise NotImplementedError("Spline arc_length")

    @staticmethod
    def get_splines():
        raise NotImplementedError("Spline get_splines")

    @staticmethod
    def distance(splines, samples):
        dist = 0
        for spline in splines:
            dist += spline.arc_length(samples)
        return dist
