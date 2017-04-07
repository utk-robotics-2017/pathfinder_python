class Segment2D:
	def __init__(self, **kwargs):
		self.x = 0
		self.y = 0
		self.angle = 0

		self.__dict__.update(kwargs)