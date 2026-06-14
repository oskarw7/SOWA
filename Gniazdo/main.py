import logging
import cv2
import queue
import subprocess
import sys
import threading
from time import sleep
import paramiko
from Camera import Camera
from Drone import Drone
from flask import Flask
from helpers import *
from Parser import InitArgsParser, Parser
from Scene import Scene



class Simulation:
    def __init__(self):
        self.Camera = None
        self.Scene = None
        self.Drone = None
        self.Parser = None
        self.Subprocesses = []
        self.args = InitArgsParser.arg_parser.parse_args()
        self.ssh = SSHManager("192.168.5.189","sowa", "12345")
    def start_remote_processes(self):
        self.ssh.connect()
        self.ssh.run_commands()

    def init_simulation(self):
        self.Scene = Scene.Scene(self)
        self.Camera = Camera.Camera(self, self.args.auto_reset)
        self.Camera.start()
        self.Drone = Drone.Drone(self)
        self.Streamer = subprocess.Popen(
            ffmpeg_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.Subprocesses.append(self.Streamer)

        if self.args.gps_server:
            threading.Thread(target=self.gps_server, daemon=True).start()

        if not self.args.ext_middle_module:
            serial_emulation = subprocess.Popen(
                emulate_serial_connection_socat_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            sleep(1)
            middle_module_proc = subprocess.Popen(["../middle-module/build/main"])
            self.Subprocesses += [serial_emulation, middle_module_proc]

        if self.args.console_control:
            console_parser = Parser.Parser(self.Camera, "console")
            console_parser.start()

        if not self.args.ext_detection:
            self.q = queue.Queue()
            # os.mkfifo("/tmp/rura")
            threading.Thread(target=sender, args=(self.q,), daemon=True).start()

        if self.args.ext_middle_module:
            parser = Parser.Parser(
                self.Camera,
                "serial",
                self.args.ext_middle_module,
                self.args.duplicate_serial,
            )
        else:
            parser = Parser.Parser(self.Camera, "serial")
        self.Parser = parser
        parser.start()

        frame = self.Camera.get_frame()

        self.Streamer.stdin.write(frame.tobytes())
        if self.args.visualize:
            self.Player = subprocess.Popen(
                [
                    "ffplay",
                    "-rtsp_transport",
                    "tcp",
                    "rtsp://localhost:8554/live.stream",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.Subprocesses.append(self.Player)
        self.Drone.start()
        self.Camera.inject_tracked_obj(self.Drone)

        threading.Thread(target=self.start_remote_processes, daemon=True).start()


    def gps_server(self):
        app = Flask(__name__)

        app.logger.disabled = True

        log = logging.getLogger("werkzeug")
        log.disabled = True
        log.setLevel(logging.ERROR)

        @app.route("/")
        def home():
            return self.Drone.get_current_nema_gps_message()
            # return bytes(self.Drone.get_current_nema_gps_message(), 'utf-8')

        app.run(port=8080)

    def start(self):
        dt = 1 / 300

        while True:
            dr_x, dr_y, dr_z = self.Drone.position
            self.Scene.overlay_object(self.Drone)
            frame, offset = self.Camera.get_frame_resolve_drone_offset(
                [int(dr_x) % self.Scene.image_width, int(dr_y)]
            )
            self.Streamer.stdin.write(frame.tobytes())

            if not self.args.ext_detection:
                self.q.put((-offset[0], offset[1]))

            # print((offset[0], offset[1]))
            # print([x-y for x,y in zip(cam.orientation, cam.orientation_target) ], cam._resolve_orientation(), offset )
            sleep(dt)


sim = Simulation()
sim.init_simulation()
try:
    sim.start()
except KeyboardInterrupt:
    sim.ssh.close()
    for process in sim.Subprocesses:
        process.kill()
        outs, errs = process.communicate()
    sys.exit()
