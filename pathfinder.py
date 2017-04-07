import shutil
import os
import argparse
import json
import csv
import sys

from structs.config import Config
from structs.waypoint import Waypoint
from trajectory_generator import TrajectoryGenerator


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
        self.wheelbase = config['wheelbase']
        self.spline_type = config['spline_type']

    def load_waypoints(self, filepath, copy=True):
        if copy:
            shutil.copyfile(filepath, "%s/waypoints.csv" % self.folder)
            os.chmod("%s/waypoints.csv" % self.folder, 0o777)
        self.waypoints = []
        with open(filepath) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.waypoints.append(Waypoint(x=row['x'], y=row['y'], angle=row['theta']))

    def save_waypoints(self):
        with open("%s/waypoints.csv" % self.folder, 'w') as csv_file:
            fieldnames = ['x', 'y', 'angle']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            for waypoint in self.waypoints:
                writer.write({'x': waypoint.x, 'y': waypoint.y, 'angle': waypoint.theta})

    def generate_trajectory(self):
        if not hasattr(self, 'trajectoryConfig'):
            print("Config file has not been loaded")
            sys.exit()

        if not hasattr(self, 'waypoints'):
            print("Waypoints file has not been loaded")
            sys.exit()

        generator = TrajectoryGenerator(self.trajectory_config, self.spline_type)
        generator.set_wheelbase(self.wheelbase)
        self.segments = generator.generate(self.waypoints)

    def write_trajectory(self):
        self.generate_trajectory()

        fieldnames = ['dt', 'distance', 'velocity', 'acceleration', 'jerk', 'angle']
        writer = csv.DictWriter("%s/trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.segments:
            writer.writerow(segment.__dict__)

    def write_tank_trajectory(self):
        if not hasattr(self, 'segments'):
            self.generate_trajectory()
        fieldnames = ['dt', 'distance', 'velocity', 'acceleration', 'jerk', 'angle']
        left_writer = csv.DictWriter("%s/left_tank_trajectory.csv" % self.folder, fieldnames=fieldnames)
        left_writer.writeheader()
        right_writer = csv.DictWriter("%s/right_tank_trajectory.csv" % self.folder, fieldnames=fieldnames)
        right_writer.writeheader()
        for segment in self.segments:
            left_writer.writerow({**segment.left.__dict__, **segment.left_2d.__dict__})
            right_writer.writerow({**segment.right.__dict__, **segment.right_2d.__dict__})

if __name__ == "__main__":
    # Collect command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--folder", required=True, help="Folder where the trajectory will be writen")
    ap.add_argument("-c", "--config", required=True, help="File containing the robot configuration/dynamics")
    ap.add_argument("-w", "--waypoints", required=True, help="File containing the waypoint")
    ap.add_argument("-t", "--tank", required=False, help="Tank trajectory will be written")
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
