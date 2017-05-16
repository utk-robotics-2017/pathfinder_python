import math
from .decorators import attr_check, type_check, void

unit_forward_declare = None


@attr_check
class Unit:
    base_value = float

    @type_check
    def __init__(self, value: (int, float), unit: (void, float)=None):
        if unit is None:
            self.base_value = float(value)
        else:
            self.base_value = float(value * unit)

    @type_check
    def to(self, unit: float) -> float:
        return self.base_value / unit

    @type_check
    def __add__(self, other: unit_forward_declare) -> unit_forward_declare:
        return Unit(self.base_value + other.base_value)

    @type_check
    def __sub__(self, other: unit_forward_declare) -> unit_forward_declare:
        return Unit(self.base_value - other.base_value)

    @type_check
    def __mul__(self, other: (float, int, unit_forward_declare)) -> unit_forward_declare:
        if isinstance(other, (float, int)):
            return Unit(self.base_value * other)
        else:
            return Unit(self.base_value * other.base_value)

    @type_check
    def __truediv__(self, other: (float, int, unit_forward_declare)) -> unit_forward_declare:
        if isinstance(other, (float, int)):
            return Unit(self.base_value / other)
        else:
            return Unit(self.base_value / other.base_value)

    @type_check
    def __iadd__(self, other: unit_forward_declare) -> unit_forward_declare:
        return Unit(self.base_value + other.base_value)

    @type_check
    def __isub__(self, other: unit_forward_declare) -> unit_forward_declare:
        return Unit(self.base_value - other.base_value)

    @type_check
    def __imul__(self, other: unit_forward_declare) -> unit_forward_declare:
        return Unit(self.base_value * other.base_value)

    @type_check
    def __itruediv__(self, other: (float, int, unit_forward_declare)) -> unit_forward_declare:
        if isinstance(other, (float, int)):
            return Unit(self.base_value / other)
        else:
            return Unit(self.base_value / other.base_value)

    @type_check
    def __neg__(self) -> unit_forward_declare:
        return Unit(-1 * self.base_value)

    @type_check
    def __pos__(self) -> unit_forward_declare:
        return Unit(self.base_value)

    @type_check
    def __abs__(self) -> unit_forward_declare:
        return Unit(abs(self.base_value))

    @type_check
    def __lt__(self, other: (float, int, unit_forward_declare)) -> bool:
        if isinstance(other, (float, int)):
            if other == 0:
                return self.base_value < 0
            else:
                raise Exception("Unit cannot be compared to value {}".format(other))
        else:
            return self.base_value < other.base_value

    @type_check
    def __le__(self, other: (float, int, unit_forward_declare)) -> bool:
        if isinstance(other, (float, int)):
            if other == 0:
                return self.base_value <= 0
            else:
                raise Exception("Unit cannot be compared to value {}".format(other))
        else:
            return self.base_value <= other.base_value

    @type_check
    def __eq__(self, other: unit_forward_declare) -> bool:
        return self.base_value == other.base_value

    @type_check
    def __ne__(self, other: unit_forward_declare) -> bool:
        return self.base_value != other.base_value

    @type_check
    def __gt__(self, other: (float, int, unit_forward_declare)) -> bool:
        if isinstance(other, (float, int)):
            if other == 0:
                return self.base_value > 0
            else:
                raise Exception("Unit cannot be compared to value {}".format(other))
        else:
            return self.base_value > other.base_value

    @type_check
    def __ge__(self, other: (float, int, unit_forward_declare)) -> bool:
        if isinstance(other, (float, int)):
            if other == 0:
                return self.base_value >= 0
            else:
                raise Exception("Unit cannot be compared to value {}".format(other))
        else:
            return self.base_value >= other.base_value

unit_forward_declare = Unit


class Constant(Unit):
    def __init__(self, value):
        Unit.__init__(self, value, 1.0)


class Length(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    m = 1.0
    mm = m * .001
    cm = m * .01
    km = m * 1000.0

    inch = m * 39.3701
    ft = inch * 12.0


Distance = Length


class Angle(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    degree = 1.0
    radian = degree * 180.0 / math.pi
    rev = degree * 360.0
    quaternion = radian * math.pi
    Q = quaternion


class Time(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    s = 1.0
    ms = s * .001
    minute = s * 60.0
    hr = minute * 60.0


class Velocity(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    m_s = Length.m / Time.s
    m_minute = Length.m / Time.minute

    mm_s = Length.mm / Time.s
    mm_minute = Length.mm / Time.minute

    cm_s = Length.cm / Time.s
    cm_minute = Length.cm / Time.minute

    inch_s = Length.inch / Time.s
    inch_minute = Length.inch / Time.minute

    ft_s = Length.ft / Time.s
    ft_minute = Length.ft / Time.minute


Speed = Velocity


class AngularVelocity(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    rpm = Angle.rev / Time.s
    rps = Angle.rev / Time.s
    rad_s = Angle.radian / Time.s
    deg_s = Angle.degree / Time.s


class Acceleration(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    m_s2 = Length.m / Time.s ** 2
    m_minute2 = Length.m / Time.minute ** 2

    mm_s2 = Length.mm / Time.s ** 2
    mm_minute2 = Length.mm / Time.minute ** 2

    cm_s2 = Length.cm / Time.s ** 2
    cm_minute2 = Length.cm / Time.minute ** 2

    inch_s2 = Length.inch / Time.s ** 2
    inch_minute2 = Length.inch / Time.minute ** 2

    ft_s2 = Length.ft / Time.s ** 2
    ft_minute2 = Length.ft / Time.minute ** 2

    G = m_s2 * 9.81
    g = G


class Jerk(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)

    m_s3 = Length.m / Time.s ** 3
    m_minute3 = Length.m / Time.minute ** 3

    mm_s3 = Length.mm / Time.s ** 3
    mm_minute3 = Length.mm / Time.minute ** 3

    cm_s3 = Length.cm / Time.s ** 3
    cm_minute3 = Length.cm / Time.minute ** 3

    inch_s3 = Length.inch / Time.s ** 3
    inch_minute3 = Length.inch / Time.minute ** 3

    ft_s3 = Length.ft / Time.s ** 3
    ft_minute3 = Length.ft / Time.minute ** 3


class Force(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    N = 1
    oz = N * 3.59694309
    lbs = oz / 16


class Pressue(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    Pa = Force.N / (Distance.m ** 2)
    kPa = Pa * 1000
    atm = Pa * 9.86923e-6
    mb = Pa * 0.01
    Hg = Pa * 3386.38866667


class Torque(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    Nm = Force.N * Distance.m
    ozinch = Force.oz * Distance.inch


class Current(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    A = 1


class Voltage(Unit):
    def __init__(self, value, unit=None):
        Unit.__init__(self, value, unit=None)
    v = 1


class Temperature(Unit):
    def __init__(self, value, unit=None):
        if unit == self.C:
            self.base_value = value
        elif unit == self.K:
            self.base_value = value - 273.15
        elif unit == self.F:
            self.base_value = (value - 32) * (5 / 9)

    def to(self, unit):
        if unit == self.C:
            return self.base_value
        elif unit == self.K:
            return self.base_value + 273.15
        elif unit == self.F:
            return (self.base_value * (9 / 5)) + 32

    C = 1
    K = 2
    F = 3

zero_unit = Unit(0)
