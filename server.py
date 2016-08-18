import sys
import random
import signal
import time
import json
import csv

import tornado.ioloop
import tornado.websocket

from Pathfinder import Pathfinder

clients = set()
clientId = 0

port = 9001
pin = random.randint(0, 99999)
pathsFolder = "/paths"
configFilepath = "%s/robotConfig.json" % pathsFolder
p = Pathfinder
def log(wsId, message):
    print("{}\tClient {:2d}\t{}".format(time.strftime("%H:%M:%S", time.localtime()), wsId, message))

class server(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        global clients, clientId

        self.id = clientId
        clientId += 1
        clients.add(self)

        self.verified = False

        log(self.id, "connected with ip: " + self.request.remote_ip)

    def on_message(self, message):
        if not self.verified:
            try:
                clientPin = int(message)
            except ValueError:
                self.write_message("Invalid Pin")
                log(self.id, "entered an invalid pin: " + message)
                return

            if clientPin == pin:
                self.verified = True
                self.write_message("Verified")
                log(self.id, "entered correct pin")
            else:
                self.write_message("WrongPin")
                log(self.id, "entered wrong pin")

        else:
            cmd = "Command"
            if message[:len(cmd)] == cmd:
                # Execute logic for Command
                # Additional logic will be in "message[len(cmd):]"
                return

            cmd = "GetConfig"
            if message[:len(cmd)] == cmd:
                if not os.path.exists(configFilepath):
                    self.write_message("[]")
                    log(self.id, "no file, sending an empty list")
                else:
                    with open(configFilepath, 'r') as jsonFile:
                        jsonData = jsonFile.read().replace('\n', '')
                        self.write_message("RobotConfig:" + jsonData)
                        log(self.id, "requested robot config")
                return

            cmd = "PostConfig"
            if message[:len(cmd)] == cmd:
                with open(configFilepath, 'w') as jsonFile:
                    jsonFile.write(message[len(cmd):])
                    p.loadConfig(configFile, False)
                    self.write_message("PostedRobotConfig")
                    log(self.id, "posted robot config")
                return

            cmd = "GetWaypoints"
            if message[:len(cmd)] == cmd:
                pathName = message[len(cmd):]
                p.loadWaypoints("%s/%s/waypoints.csv" % (pathsFolder, pathName), False)
                waypointsJson = json.dumps(p.waypoints).replace('\n', '')
                self.write_message("Waypoints:"+waypointsJson)
                log(self.id, "request waypoints for %s" % pathName)
                return

            cmd = "GetTrajectories"
            if message[:len(cmd)] == cmd:
                waypointsJson = message[len(cmd):]
                p.waypoints = json.loads(waypointsJson)
                response = dict()
                p.generateTrajectory()
                response['trajectory'] = p.segments
                if p.drivebaseType == DrivebaseType.TANK:
                    p.generateTankTrajectory()
                    response['tank_left_trajectory'] = p.tank_left_segments
                    response['tank_right_trajectory'] = p.tank_right_segments
                elif p.drivebaseType == DrivebaseType.SWERVE:
                    p.generateSwerveTrajectory()
                    response['swerve_front_left_trajectory'] = p.swerve_front_left_segments
                    response['swerve_front_right_trajectory'] = p.swerve_front_right_segments
                    response['swerve_back_left_trajectory'] = p.swerve_back_left_segments
                    response['swerve_back_right_trajectory'] = p.swerve_back_right_segments
                else:
                    print "Unknown Database Type"

                self.write_message("Trajectories:" + json.dumps(response).replace('\n', '')
                log(self.id, "request for trajectories")
                return

            cmd = "SavePath"
            if message[:len(cmd)] == cmd:
                messageJson = json.loads(message[len(cmd):])
                p.waypoints = messageJson['waypoints']
                p.setFolder("%s/%s" % (pathsFolder, messageJson['pathName']))
                p.saveWaypoints()
                p.writeTrajectory()
                if p.drivebaseType == DrivebaseType.TANK:
                    p.writeTankTrajectory()
                elif p.drivebaseType == DrivebaseType.SWERVE:
                    p.writeSwerveTrajectory()
                else:
                    print "Unknown Drivebase Type"

                return

    def on_close(self):
        clients.remove(self)
        log(self.id, "disconnected")

def make_app():
    return tornado.web.Application([
        (r"/", server)
    ])

def sigInt_handler(signum, frame):
    print(" Closing Server")

    while clients:
        client = next(iter(clients))
        client.close(reason="Server Closing")
        client.on_close()

    tornado.ioloop.IOLoop.current().stop()
    print("Server is closed")
    sys.exit(0)

if __name__ == "__main__":
    app = make_app()
    app.listen(port)
    signal.signal(signal.SIGINT, sigInt_handler)
    print("Pin: {:05d}".format(pin))
    tornado.ioloop.IOLoop.current().start()
