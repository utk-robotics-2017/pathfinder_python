import shutil
import os
import argparse
import json
import csv
import sys
from enum import Enum

from Structs.TrajectoryConfig import TrajectoryConfig
from Structs.Waypoint import Waypoint
from TrajectoryGenerator import TrajectoryGenerator
from SwerveModifier import SwerveModifier
from TankModifier import TankModifier


class DrivebaseType(Enum):
    TANK = 0
    SWERVE = 1


class Pathfinder:
    def setFolder(self, folder):
        self.folder = folder

    def setupFolder(self):
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.makedirs(self.folder, 0777)
        os.chmod(self.folder, 0777)

    def loadConfig(self, filepath, copy=True):
        if copy:
            shutil.copyfile(filepath, "%s/robotConfig.json" % self.folder)
            os.chmod("%s/robotConfig.json" % self.folder, 077)

        json_file = open(filepath)
        file_text = json_file.read()
        config = json.loads(file_text)
        self.trajectoryConfig = TrajectoryConfig()
        self.trajectoryConfig.max_v = config['max_velocity']
        self.trajectoryConfig.max_a = config['max_acceleration']
        self.trajectoryConfig.max_j = config['max_jerk']
        self.trajectoryConfig.dt = config['time_step']
        self.trajectoryConfig.sample_count = config['sample_count']
        self.wheelbaseWidth = config['wheelbase_width']
        self.wheelbaseLength = config['wheelbase_length']
        self.splineType = config['splineType']
        self.drivebaseType = config['drivebaseType']

    def loadWaypoints(self, filepath, copy=True):
        if copy:
            shutil.copyfile(filepath, "%s/waypoints.csv" % self.folder)
            os.chmod("%s/waypoints.csv" % self.folder, 077)
        self.waypoints = []
        with open(filepath) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.waypoints.append(Waypoint(x=row['x'], y=row['y'], theta=row['theta']))

    def saveWaypoints(self):
        with open("%s/waypoints.csv" % self.folder, 'w') as csv_file:
            fieldnames = ['x', 'y', 'theta']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            for waypoint in self.waypoints:
                writer.write({'x': waypoint.x, 'y': waypoint.y, 'theta': waypoint.theta})

    def generateTrajectory(self):
        if not hasattr(self, 'trajectoryConfig'):
            print "Config file has not been loaded"
            sys.exit()

        if not hasattr(self, 'waypoints'):
            print "Waypoints file has not been loaded"
            sys.exit()

        generator = TrajectoryGenerator(self.waypoints, self.trajectoryConfig, self.splineType)
        self.segments = generator.generate()

    def writeTrajectory(self):

        self.generateTrajectory()

        fieldnames = ['dt', 'x', 'y', 'displacement', 'velocity', 'acceleration', 'jerk', 'heading']
        writer = csv.DictWriter("%s/trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.segments:
            writer.writerow(segment.__dict__)

    def generateTankTrajectory(self):
        if not hasattr(self, 'segments'):
            self.generateTrajectory()

        tankModifier = TankModifier(self.segments, self.wheelbase_width)
        self.tank_left_segments = tankModifier.get_left_trajectory()
        self.tank_right_segments = tankModifier.get_right_trajectory()

    def writeTankTrajectory(self):
        self.generateTankTrajectory()
        fieldnames = ['dt', 'x', 'y', 'displacement', 'velocity', 'acceleration', 'jerk', 'heading']
        writer = csv.DictWriter("%s/left_tank_trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.tank_left_segments:
            writer.writerow(segment.__dict__)

        writer = csv.DictWriter("%s/right_tank_trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.tank_right_segments:
            writer.writerow(segment.__dict__)

    def generateSwerveTrajectory(self):
        if not hasattr(self, 'segments'):
            self.generateTrajectory()

        swerveModifier = SwerveModifier(self.segments, self.wheelbase_width, self.wheelbase_length)
        self.swerve_front_left_segments = swerveModifier.get_front_left_trajectory()
        self.swerve_front_right_segments = swerveModifier.get_front_right_trajectory()
        self.swerve_back_left_segments = swerveModifier.get_back_left_trajectory()
        self.swerve_back_right_segments = swerveModifier.get_back_right_trajectory()

    def writeSwerveTrajectory(self):
        self.generateSwerveTrajectory()
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
    p.setFolder(args['folder'])
    p.setupFolder()
    p.loadConfig(args['config'])
    p.loadWaypoints(args['waypoints'])
    p.writeTrajectory()
    if(args['tank']):
        p.writeTankTrajectory()
    if(args['swerve']):
        p.writeSwerveTrajectory()
