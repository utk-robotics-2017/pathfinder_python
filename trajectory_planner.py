class TrajectoryPlanner:
	def __init__(self, splines, config):
		self.splines = splines
		self.config = config

		self.total_distance = Spline.distance(splines)

	def calculate(self, t, previous_segment=None):
		if previous_segment is None:
			previous_segment = CoupledSegment()

		current_distance = previous_segment.center.distance

		if current_distance >= self.total_distance:
			return

		# target spline is our current starting spline
		target_spline = 0
