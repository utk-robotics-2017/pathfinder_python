class CoupledSegment:
	def __init__(self, **kwargs):
		# Segment
		self.center = Segment()
		self.left = Segment()
		self.right = Segment()

		#Segment2D
		self.center_2d = Segment2D()
		self.left_2d = Segment2D()
		self.right_2d = Segment2D()

		self.__dict__.update(kwarg)