import math
import copy

class TankModifier:
    def __init__(self, original, wheelbase_width):
        self.original = original
        self.wheelbase_width = wheelbase_width
        self.modify()

    def modify(self):
        w = self.wheelbase_width / 2

        self.left_traj = []
        self.right_traj = []

        for i in range(len(self.original)):
            seg = self.original[i]
            left = copy.deepcopy(seg)
            right = copy.deepcopy(seg)

            cos_angle = math.cos(seg.heading)
            sin_angle = math.sin(seg.heading)

            left.x = seg.x - (w * sin_angle)
            left.y = seg.y + (w * cos_angle)

            if(i > 0):
                last = self.left_traj[i - 1]
                distance = math.sqrt((left.x - last.x) * (left.x - last.x) + (left.y - last.y) * (left.y - last.y))

                left.displacement += distance
                left.velocity = distance / seg.dt
                left.acceleration = (left.velocity - last.velocity) / seg.dt
                left.jerk = (left.acceleration - last.acceleration) / seg.dt

            right.x = seg.x + (w * sin_angle)
            right.y = seg.y - (w * cos_angle)
            if (i > 0):
                last = self.right_traj[i - 1]
                distance = math.sqrt((right.x - last.x) * (right.x - last.x) + (right.y - last.y) * (right.y - last.y))

                right.displacement += distance
                right.velocity = distance / seg.dt
                right.acceleration = (right.velocity - last.velocity) / seg.dt
                right.jerk = (right.acceleration - last.acceleration) / seg.dt

            self.left_traj.append(left)
            self.right_traj.append(right)

    def get_original_trajectory(self):
        return self.original

    def get_left_trajectory(self):
        return self.left_traj

    def get_right_trajectory(self):
        return self.right_traj
