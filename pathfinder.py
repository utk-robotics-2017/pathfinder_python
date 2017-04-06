import shutil
import os
import argparse
import json
import csv
import sys
from enum import Enum

from structs.trajectoryConfig import TrajectoryConfig
from structs.waypoint import Waypoint
from trajectory_generator import TrajectoryGenerator
from swerve_modifier import SwerveModifier
from tank_modifier import TankModifier


class DrivebaseType(Enum):
    TANK = 0
    SWERVE = 1


class Pathfinder:
    def set_folder(self, folder):
        self.folder = folder
        self.setup_folder()

    def setup_folder(self):
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.makedirs(self.folder, 0o777)
        os.chmod(self.folder, 0o777)

    def load_config(self, filepath, copy=True):
        if copy:
            shutil.copyfile(filepath, "%s/robot_config.json" % self.folder)
            os.chmod("%s/robot_config.json" % self.folder, 0o777)

        json_file = open(filepath)
        file_text = json_file.read()
        config = json.loads(file_text)
        self.trajectory_config = TrajectoryConfig(**config)
        self.wheelbase_width = config['wheelbase_width']
        self.wheelbase_length = config['wheelbase_length']
        self.spline_type = config['spline_type']
        self.drivebase_type = config['drivebase_type']

    def load_waypoints(self, filepath, copy=True):
        if copy:
            shutil.copyfile(filepath, "%s/waypoints.csv" % self.folder)
            os.chmod("%s/waypoints.csv" % self.folder, 0o777)
        self.waypoints = []
        with open(filepath) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.waypoints.append(Waypoint(x=row['x'], y=row['y'], theta=row['theta']))

    def save_waypoints(self):
        with open("%s/waypoints.csv" % self.folder, 'w') as csv_file:
            fieldnames = ['x', 'y', 'theta']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            for waypoint in self.waypoints:
                writer.write({'x': waypoint.x, 'y': waypoint.y, 'theta': waypoint.theta})

    def generate_trajectory(self):
        if not hasattr(self, 'trajectoryConfig'):
            print("Config file has not been loaded")
            sys.exit()

        if not hasattr(self, 'waypoints'):
            print("Waypoints file has not been loaded")
            sys.exit()

        generator = TrajectoryGenerator(self.waypoints, self.trajectory_config, self.spline_type)
        self.segments = generator.generate()

    def write_trajectory(self):
        self.generate_trajectory()

        fieldnames = ['dt', 'displacement', 'velocity', 'acceleration', 'jerk', 'heading']
        writer = csv.DictWriter("%s/trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.segments:
            writer.writerow(segment.__dict__)

    def generate_tank_trajectory(self):
        if not hasattr(self, 'segments'):
            self.generate_trajectory()

        tank_modifier = TankModifier(self.segments, self.wheelbase_width)
        self.tank_left_segments = tank_modifier.get_left_trajectory()
        self.tank_right_segments = tank_modifier.get_right_trajectory()

    def write_tank_trajectory(self):
        self.generate_tank_trajectory()
        fieldnames = ['dt', 'x', 'y', 'displacement', 'velocity', 'acceleration', 'jerk', 'heading']
        writer = csv.DictWriter("%s/left_tank_trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.tank_left_segments:
            writer.writerow(segment.__dict__)

        writer = csv.DictWriter("%s/right_tank_trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.tank_right_segments:
            writer.writerow(segment.__dict__)

    def generate_swerve_trajectory(self):
        if not hasattr(self, 'segments'):
            self.generate_trajectory()

        swerve_modifier = SwerveModifier(self.segments, self.wheelbase_width, self.wheelbase_length)
        self.swerve_front_left_segments = swerve_modifier.get_front_left_trajectory()
        self.swerve_front_right_segments = swerve_modifier.get_front_right_trajectory()
        self.swerve_back_left_segments = swerve_modifier.get_back_left_trajectory()
        self.swerve_back_right_segments = swerve_modifier.get_back_right_trajectory()

    def write_swerve_trajectory(self):
        self.generate_swerve_trajectory()
        fieldnames = ['dt', 'x', 'y', 'displacement', 'velocity', 'acceleration', 'jerk', 'heading']
        writer = csv.DictWriter("%s/swerve_front_left_trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.swerve_front_left_segments:
            writer.writerow(segment.__dict__)

        writer = csv.DictWriter("%s/swerve_front_right_trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.swerve_front_right_segments:
            writer.writerow(segment.__dict__)
        writer = csv.DictWriter("%s/swerve_back_left_trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.swerve_back_left_segments:
            writer.writerow(segment.__dict__)
        writer = csv.DictWriter("%s/swerve_back_right_trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.swerve_back_right_segments:
            writer.writerow(segment.__dict__)


if __name__ == "__main__":
    # Collect command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--folder", required=True, help="Folder where the trajectory will be writen")
    ap.add_argument("-c", "--config", required=True, help="File containing the robot configuration/dynamics")
    ap.add_argument("-w", "--waypoints", required=True, help="File containing the waypoint")
    ap.add_argument("-t", "--tank", required=False, help="Tank trajectory will be written")
    ap.add_argument("-s", "--swerve", required=False, help="Swerve trajectory will be written")
    args = vars(ap.parse_args())

    p = Pathfinder()
    p.set_folder(args['folder'])
    p.load_config(args['config'])
    p.load_waypoints(args['waypoints'])
    p.write_trajectory()
    if(args['tank']):
        p.write_tank_trajectory()
    if(args['swerve']):
        p.write_swerve_trajectory()
