from .segment import Segment
from .segment_2d import Segment2D
from util.decorators import attr_check

@attr_check
class CoupledSegment:

	center = Segment
	left = Segment
	right = Segment

	center_2d = Segment2D
	left_2d = Segment2D
	right_2d = Segment2D

	def __init__(self, **kwargs):
		# Segment
		self.center = kwargs.get('center', Segment())
		self.left = kwargs.get('left', Segment())
		self.right = kwargs.get('right', Segment())

		#Segment2D
		self.center_2d = kwargs.get('center_2d', Segment2D())
		self.left_2d = kwargs.get('left_2d', Segment2D())
		self.right_2d = kwargs.get('right_2d', Segment2D())