from Structs.TrajectoryInfo import TrajectoryInfo
from Structs.Segment import Segment
import math


class TrajectoryPlanner:
    def __init__(self, config):
        self.config = config
        self.info = None

    def prepare(self):
        max_a2 = self.config.max_a * self.config.max_a
        max_j2 = self.config.max_j * self.config.max_j

        checked_max_v = min(self.config.max_v,
                            (-max_a2 + math.sqrt(max_a2 * max_a2 + 4 *
                             (max_j2 * self.config.max_a * self.config.dest_pos))) /
                            (2 * self.config.max_j))

        filter1 = int(math.ceil((checked_max_v / self.config.max_a) / self.config.dt))
        filter2 = int(math.ceil((self.config.max_a / self.config.max_j) / self.config.dt))

        impulse = (self.config.dest_pos / checked_max_v) / self.config.dt
        time = int(math.ceil(filter1 + filter2 + impulse))

        self.info = TrajectoryInfo(filter1, filter2, time, self.config.dt, 0, checked_max_v, impulse)

    def create(self):
        segments = self.plan_fromSecondOrderFilter()

        d_theta = self.config.dest_theta - self.config.src_theta
        for i in range(self.info.length):
            segments[i].heading = self.config.src_theta + d_theta *\
                segments[i].displacement / (segments[-1].displacement)

        return segments

    def plan_fromSecondOrderFilter(self):
        last_section = Segment(self.info.dt, 0.0, 0.0, 0.0, self.info.u, 0.0, 0.0, 0.0)

        f1_buffer = []
        f1_buffer.append((self.info.u / self.info.v) * self.info.filter1)

        segments = []

        impulse = self.info.impulse
        for i in range(self.info.length):
            input_ = min(impulse, 1)

            if input_ < 1:
                input_ = input_ - 1
                impulse = 0
            else:
                impulse = impulse - input_

            f1_last = 0.0
            if i > 0:
                f1_last = f1_buffer[i - 1]
            else:
                f1_last = f1_buffer[0]

            if i < len(f1_buffer):
                f1_buffer[i] = max(0.0, min(self.info.filter1, f1_last + input_))
            else:
                f1_buffer.append(max(0.0, min(self.info.filter1, f1_last + input_)))

            f2 = 0.0

            for j in range(self.info.filter2):
                if i - j < 0:
                    break
                f2 = f2 + f1_buffer[i - j]

            f2 = f2 / self.info.filter1

            seg = Segment(dt=self.info.dt, x=0.0, y=0.0, displacement=0.0,
                          velocity=0.0, acceleration=0.0, jerk=0.0, heading=0.0)
            seg.velocity = f2 / self.info.filter2 * self.info.v
            seg.displacement = (last_section.velocity + seg.velocity) / 2.0 * seg.dt + last_section.displacement
            seg.x = seg.displacement
            seg.y = 0.0
            seg.acceleration = (seg.velocity - last_section.velocity) / seg.dt
            seg.jerk = (seg.acceleration - last_section.acceleration) / seg.dt

            segments.append(seg)
            last_section = seg

        return segments
