#includes
import argparse
import json
import csv
import sys
from Structs.TrajectoryConfig import TrajectoryConfig
from Structs.Waypoint import Waypoint
from SplineGenerator import FitType
from TrajectoryGenerator import TrajectoryGenerator
from SwerveModifier import SwerveModifier
from TankModifier import TankModifier

def write_trajectory(file_, segments):
    fieldnames = ['dt', 'x', 'y', 'position', 'velocity', 'acceleration', 'jerk', 'heading']
    writer = csv.DictWriter(file_, fieldnames=fieldnames)
    writer.writeheader()
    for segment in segments:
        print "%f %f %f %f %f %f %f %f" % (segment.dt, segment.x, segment.y, segment.position, segment.velocity, segment.acceleration, segment.jerk, segment.heading)
        writer.writerow({'dt': segment.dt, 'x': segment.x, 'y': segment.y, 'position': segment.position, 'velocity': segment.velocity, 'acceleration': segment.acceleration, 'jerk': segment.jerk, 'heading': segment.heading})


# Collect command line arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--config", required=False, help="Path to the config file")
ap.add_argument("-w", "--waypoints", required=False, help="Path to the waypoints file")
ap.add_argument("-o", "--output", required=False, help="Path to the output file that contains the trajectory")
args = vars(ap.parse_args())

# Set up the input and out files
if args['config'] is not None:
    config_file = open(args['config'], "r")
else:
    config_file = open("pathfinder_config.json", "r")

if args['waypoints'] is not None:
    waypoints_file = open(args['waypoints'])
else:
    waypoints_file = open("waypoints.csv")

if args['output'] is not None:
    output_file = open(args['output'], "w")
else:
    output_file = open("trajectory.csv", "w")

# Read in json
file_text = ""
for line in config_file:
    file_text = file_text + line
config_json = json.loads(file_text)

config = TrajectoryConfig()
config.max_v = config_json['max_velocity']
config.max_a = config_json['max_acceleration']
config.max_j = config_json['max_jerk']
config.dt = config_json['delta_time']
config.sample_count = config_json['sample_count']

waypoints = []
reader = csv.DictReader(waypoints_file)
for row in reader:
    waypoints.append(Waypoint(float(row['x']), float(row['y']), float(row['theta'])))
if config_json['fit_type'] == "Cubic":
    generator = TrajectoryGenerator(waypoints, config, fit_type=FitType.CUBIC)
elif config_json['fit_type'] == "QUINTIC":
    generator = TrajectoryGenerator(waypoints, config, fit_type=FitType.QUINTIC)
trajectory_segments = generator.generate()

write_trajectory(output_file, trajectory_segments)

drivetrain = config_json['drivetrain']

if drivetrain == 'Tank':
    tankModifier = TankModifier(trajectory_segments, config_json['wheelbase_width'])

    left_segments = tankModifier.get_left_trajectory()
    right_segments = tankModifier.get_right_trajectory()

    if args['output'] is not None:
        left_output_file = open("left_" + args['output'], "w")
        right_output_file = open("right_" + args['output'], "w")
    else:
        left_output_file = open("left_trajectory.csv", "w")
        right_output_file = open("right_trajectory.csv", "w")

    write_trajectory(left_output_file, left_segments)
    write_trajectory(right_output_file, right_segments)

elif drivetrain == 'Swerve':
    swerveModifier = SwerveModifier(trajectory_segments, config_file['wheelbase_width'], config_file['wheelbase_length'])

    front_left_segments = swerveModifier.get_front_left_trajectory()
    front_right_segments = swerveModifier.get_front_right_trajectory()
    back_left_segments = swerveModifier.get_back_left_trajectory()
    back_right_segments = swerveModifier.get_back_right_trajectory()

    if args['output'] is not None:
        front_left_output_file = open("front_left_" + args['output'], "w")
        front_right_output_file = open("front_right_" + args['output'], "w")
        back_left_output_file = open("back_left_" + args['output'], "w")
        back_right_output_file = open("back_right_" + args['output'], "w")
    else:
        front_left_output_file = open("front_left_trajectory.csv", "w")
        front_right_output_file = open("front_right_trajectory.csv", "w")
        back_left_output_file = open("back_left_trajectory.csv", "w")
        back_right_output_file = open("back_right_trajectory.csv", "w")

    write_trajectory(front_left_output_file, front_left_segments)
    write_trajectory(front_right_output_file, front_right_segments)
    write_trajectory(back_left_output_file, back_left_segments)
    write_trajectory(back_right_output_file, back_right_segments)
else:
    print "Error: Unknown drivetrain in config file"
    sys.exit()

