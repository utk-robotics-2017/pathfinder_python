import shutil
import os
import argparse
import json
import csv
import sys

from structs.config import Config
from structs.waypoint import Waypoint
from trajectory_generator import TrajectoryGenerator

from util.decorators import singleton, attr_check, type_check, void
from util.units import Distance
from util.logger import Logger
logger = Logger()

@attr_check
class Pathfinder:
    ''' The main class for generating discretized splines for path
        following based on waypoints and robot dynamics

        Attributes
        ----------
        folder: str
            The name of the folder in which output is written
        trajectory_config: TrajectoryConfig
            Configuration struct containing dynamics of the robot and parameters
            for the spline generation.
        wheelbase: Distance
            The distance between the left side and right side wheels
        spline_type: int
            An integer representing the enumeration of the type of spline to use.
        waypoints: list(Waypoint)
            A list of the Waypoint structs used for generating the trajectory.

    '''

    folder = str
    trajectory_config = Config
    wheelbase = Distance
    spline_type = int
    waypoints = list


    def set_folder(self, folder):
        self.folder = folder
        self.setup_folder()

    @type_check
    def setup_folder(self) -> void:
        ''' Removes the folder if it exists and creates a new one with
            completely open privileges.
        '''
        if os.path.exists(self.folder):
            shutil.rmtree(self.folder)
        os.makedirs(self.folder, 0o777)
        os.chmod(self.folder, 0o777)

    @type_check
    def load_config(self, filepath: str, copy: bool=True) -> void:
        ''' Loads the configuration file containing the robot dynamics
            and spine type.

            Parameters
            ----------
            filepath: str
                The path to the config file

            copy: bool
                Whether to copy the config file into the output folder.
                Default is true.

        '''
        if copy:
            shutil.copyfile(filepath, "%s/robot_config.json" % self.folder)
            os.chmod("%s/robot_config.json" % self.folder, 0o777)

        with open(filepath) as json_file:
            file_text = json_file.read()
        config = json.loads(file_text)
        self.trajectory_config = Config(**config)
        self.wheelbase = Distance(config['wheelbase'])
        self.spline_type = config['spline_type']

    @type_check
    def load_waypoints(self, filepath: str, copy: bool=True) -> void:
        ''' Loads the waypoints file.

            Parameters
            ----------
            filepath: str
                The path to the waypoints file

            copy: bool
                Whether to copy the waypoints file into the output folder.
                Default is true.

        '''
        if copy:
            shutil.copyfile(filepath, "%s/waypoints.csv" % self.folder)
            os.chmod("%s/waypoints.csv" % self.folder, 0o777)
        self.waypoints = []
        with open(filepath) as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                self.waypoints.append(Waypoint(x=row['x'], y=row['y'], angle=row['theta']))

    @type_check
    def save_waypoints(self) -> void:
        ''' Saves the waypoints as a csv to a file in the output folder.
        '''
        with open("%s/waypoints.csv" % self.folder, 'w') as csv_file:
            fieldnames = ['x', 'y', 'angle']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            for waypoint in self.waypoints:
                writer.write({'x': waypoint.x, 'y': waypoint.y, 'angle': waypoint.theta})

    @type_check
    def generate_trajectory(self) -> void:
        ''' Generates the trajectory based on the config and waypoints.

        '''
        if not hasattr(self, 'trajectory_config'):
            logger.error("Config file has not been loaded")
            sys.exit()

        if not hasattr(self, 'waypoints'):
            logger.error("Waypoints file has not been loaded")
            sys.exit()

        generator = TrajectoryGenerator(self.trajectory_config, self.spline_type)
        generator.set_wheelbase(self.wheelbase)
        self.segments = generator.generate(self.waypoints)

    @type_check
    def write_trajectory(self) -> void:
        ''' Writes the center trajectory to a file in the output folder.
        '''
        if not hasattr(self, 'segments'):
            self.generate_trajectory()

        fieldnames = ['dt', 'distance', 'velocity', 'acceleration', 'jerk', 'angle']
        writer = csv.DictWriter("%s/trajectory.csv" % self.folder, fieldnames=fieldnames)
        writer.writeheader()
        for segment in self.segments:
            writer.writerow(segment.__dict__)

    @type_check
    def write_tank_trajectory(self) -> void:
        ''' Writes the trajectory for the left and right sides of a tank drive to a file
            in the output folder.
        '''
        if not hasattr(self, 'segments'):
            self.generate_trajectory()
        
        fieldnames = ['dt', 'distance', 'velocity', 'acceleration', 'jerk', 'angle']
        
        left_writer = csv.DictWriter("%s/left_tank_trajectory.csv" % self.folder, fieldnames=fieldnames)
        left_writer.writeheader()
        
        right_writer = csv.DictWriter("%s/right_tank_trajectory.csv" % self.folder, fieldnames=fieldnames)
        right_writer.writeheader()
        
        for segment in self.segments:
            left_writer.writerow({**segment.left.__dict__(), **segment.left_2d.__dict__()})
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
