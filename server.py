import sys
import random
import signal
import time

import tornado.ioloop
import tornado.websocket

clients = set()
clientId = 0

port = 9000
pin = random.randint(0, 99999)

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
