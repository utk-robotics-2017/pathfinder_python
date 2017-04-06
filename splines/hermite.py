from enum import IntEnum
import numpy as np
import math
from .spine import Spline, SplineType


class Hermite(Spline):
	def __init__(self, type_, start, end):
		self.type_ = type_
		self.start = start
		self.end = end

		self.x_offset = start.x
		self.y_offset = start.y

		dy = end.y - start.y
		dx = end.x - start.x

		self.angle_offset = math.atan2(dy, dx)
		self.hyp_distance = math.sqrt(dx ** 2 + dy ** 2)
		self.tangent0 = math.tan(start.angle - self.angle_offset)
		self.tangent1 = math.tan(end.angle - self.angle_offset)
		self.a = self.tangent0 * hyp_distance
		self.b = self.tangent1 * hyp_distance

		# Cache the arc calc to save time
		self.last_arc_calc = 0
		self.last_arc_calc_samples = 0

	def calculate(self, t):
		coord = SplineCoord(time=t)
		x = self.hyp_distance * t
		y = 0
		if self.type_ == SplineType.HERMITE_CUBIC:
			y = self.a * (t ** 3 - 2 * t ** 2 + t) + b * (t ** 3 - t ** 2)
		# TODO: QUINTIC

		# Translate back to global
		coord.x = x * math.cos(self.angle_offset) - y * math.sin(self.angle_offset) + self.x_offset
		coord.y = x * math.sin(self.angle_offset) - y * math.cos(self.angle_offset) + self.y_offset

		def bound_radians(angle):
			new_angle = math.fmod(angle, 2 * 3.14159265)
			if new_angle < 0:
				new_angle = 2 * 3.14159265 + new_angle
			return new_angle

		coord.angle = bound_radians(math.atan(self.derive(t)) + self.angle_offset)

		return coord

	def deriv(self, t):
		return a * (3 * t ** 2 - 4 * t + 1) + b * (3 * t  ** 2 - 2 * t)

	def arc_length(self, samples):
		if self.last_arc_calc_samples != samples:
			t = 0
			dt = 1 / samples

			dydt = self.deriv(t)
			integrand = 0
        	arc_length = 0
        	last_integrand = math.sqrt(1 + dydt ** 2) * dt

        	# [0, 1)
        	for t in np.arange(0, 1, dt):
        		dydt = self.deriv(t)
            	integrand = math.sqrt(1 + dydt ** 2) * dt
            	arc_length += (integrand + last_integrand) / 2
            	last_integrand = integrand
            dydt = self.deriv(1)
            integrand = math.sqrt(1 + dydt ** 2) * dt
            arc_length += (integrand + last_integrand) / 2
            last_integrand = integrand

        	last_arc_calc_samples = samples
        	last_arc_calc = self.hyp_distance * arc_length
        return last_arc_calc;


	@staticmethod
	def get_splines(type_, waypoints):
		splines = []
		for i in enumerate(len(waypoints) - 1):
			splines.add(Hermite(type_, waypoints[i], waypoints[i + 1]))