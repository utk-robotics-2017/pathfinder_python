import os
import sys
import random
import signal
import time
import json

import tornado.ioloop
import tornado.websocket
import tornado.httpserver

from Pathfinder import Pathfinder, DrivebaseType

clients = set()
clientId = 0

port = 9001
pin = random.randint(0, 99999)
pathsFolder = "/Robot/Trajectories"
configFilepath = "{0:s}/robotConfig.json".format(pathsFolder)
p = Pathfinder


def log(wsId, message):
    print("{0:s}\tClient {1:2d}\t{2:s}".format(time.strftime("%H:%M:%S", time.localtime()), wsId, message))


class Server(tornado.websocket.WebSocketHandler):
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
            cmd = "GetConfig"
            if message[:len(cmd)] == cmd:
                if not os.path.exists(configFilepath):
                    self.write_message("{}")
                    log(self.id, "no file, sending an empty object")
                else:
                    with open(configFilepath, 'r') as jsonFile:
                        jsonData = jsonFile.read().replace('\n', '')
                        self.write_message("RobotConfig" + jsonData)
                        log(self.id, "requested robot config")
                return

            cmd = "PostConfig"
            if message[:len(cmd)] == cmd:
                with open(configFilepath, 'w') as jsonFile:
                    jsonFile.write(message[len(cmd):])
                    p.loadConfig(configFilepath, False)
                    self.write_message("PostedRobotConfig")
                    log(self.id, "posted robot config")
                return

            cmd = "GetWaypoints"
            if message[:len(cmd)] == cmd:
                pathName = message[len(cmd):]
                p.loadWaypoints("{}/{}/waypoints.csv".format(pathsFolder, pathName), False)
                waypointsJson = json.dumps([w.__dict__ for w in p.waypoints]).replace('\n', '')
                self.write_message("Waypoints" + waypointsJson)
                log(self.id, "requested waypoints for " + pathName)
                return

            cmd = "PostWaypoints"
            if message[:len(cmd)] == cmd:
                data = json.loads(message[len(cmd):])
                pathName = data["name"]
                waypoints = data["waypoints"]

                filename = "{}/{}/waypoints.csv".format(pathsFolder, pathName)
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, "w") as f:
                    f.write("x,y,theta\n")
                    for w in waypoints:
                        f.write("{},{},{}\n".format(w['x'], w['y'], w['r']))
                log(self.id, "posted waypoints for " + pathName)

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
                    print("Unknown Database Type")

                self.write_message("Trajectories:" + json.dumps(response).replace('\n', ''))
                log(self.id, "request for trajectories")
                return

            cmd = "SavePath"
            if message[:len(cmd)] == cmd:
                messageJson = json.loads(message[len(cmd):])
                p.waypoints = messageJson['waypoints']
                p.setFolder("{}/{}".format(pathsFolder, messageJson['pathName']))
                p.saveWaypoints()
                p.writeTrajectory()
                if p.drivebaseType == DrivebaseType.TANK:
                    p.writeTankTrajectory()
                elif p.drivebaseType == DrivebaseType.SWERVE:
                    p.writeSwerveTrajectory()
                else:
                    print("Unknown Drivebase Type")

                return

    def on_close(self):
        clients.remove(self)
        log(self.id, "disconnected")


class SetupTLS(tornado.web.RequestHandler):
    def get(self):
        self.write("TLS certificate has been accepted, please try the websocket again.")


def make_app():
    return tornado.httpserver.HTTPServer(tornado.web.Application([
        (r"/", Server),
        (r"/setuptls", SetupTLS)
    ]), ssl_options={
        "certfile": "/etc/ssl/certs/tornado.crt",
        "keyfile": "/etc/ssl/certs/tornado.key"
    })


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
