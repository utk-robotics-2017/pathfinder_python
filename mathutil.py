import math


# Bound an angle (in degrees) to -180 to 180 degrees.
def boundHalfDegress(angle_degrees):
    while angle_degrees >= 180.0:
        angle_degrees = angle_degrees - 360.0

    while angle_degrees < 180.0:
        angle_degrees = angle_degrees + 360.0
    return angle_degrees


def bound_radians(angle):
    TAU = 2 * 3.14159265358979323846
    new_angle = math.fmod(angle, TAU)
    if (new_angle < 0):
        new_angle = TAU + new_angle
    return new_angle
