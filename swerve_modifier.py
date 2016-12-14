import copy


class SwerveModifier:
    def __init__(self, original, wheelbase_width, wheelbase_depth):
        self.original = original
        self.wheelbase_width = wheelbase_width
        self.wheelbase_depth = wheelbase_depth
        self.modify()

    def modify(self):
        self.front_left = []
        self.front_right = []
        self.back_left = []
        self.back_right = []

        for i in range(len(self.original)):
            seg = self.original[i]
            fl = copy.deepcopy(seg)
            fr = copy.deepcopy(seg)
            bl = copy.deepcopy(seg)
            br = copy.deepcopy(seg)

            fl.x = seg.x - self.wheelbase_width / 2
            fl.y = seg.y + self.wheelbase_depth / 2
            fr.x = seg.x + self.wheelbase_width / 2
            fr.y = seg.y + self.wheelbase_depth / 2

            bl.x = seg.x - self.wheelbase_width / 2
            bl.y = seg.y - self.wheelbase_depth / 2
            br.x = seg.x + self.wheelbase_width / 2
            br.y = seg.y - self.wheelbase_depth / 2

            self.front_left.append(fl)
            self.front_right.append(fr)
            self.back_left.append(bl)
            self.back_right.append(br)

    def get_original_trajectory(self):
        return self.original

    def get_front_left_trajectory(self):
        return self.front_left

    def get_front_right_trajectory(self):
        return self.front_right

    def get_back_left_trajectory(self):
        return self.back_left

    def get_back_right_trajectory(self):
        return self.back_right
