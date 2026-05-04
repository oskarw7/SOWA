import queue
import subprocess
import threading
from time import sleep, time
import sys
import cv2
import subprocess
from Camera import Camera
from Drone import Drone
from Scene import Scene
from time import sleep
from helpers import *
import threading
from Parser import Parser,InitArgsParser
from helpers import *
import os
import queue

class Simulation():
    
    
    def __init__(self):
        self.Camera =None
        self.Scene =None
        self.Drone =None
        self.Parser = None
        self.Subprocesses = []
        self.args = InitArgsParser.arg_parser.parse_args()

    def init_simulation(self):
        self.Scene = Scene.Scene(self)
        self.Camera = Camera.Camera(self,self.args.auto_reset)
        self.Camera.start()
        self.Drone = Drone.Drone(self)
        self.Streamer = subprocess.Popen(ffmpeg_cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL) 
        self.Subprocesses.append(self.Streamer) 
        if not self.args.ext_middle_module:
            serial_emulation = subprocess.Popen(emulate_serial_connection_socat_cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            sleep(1)
            middle_module_proc = subprocess.Popen(["../middle-module/build/main"])
            self.Subprocesses += [serial_emulation,middle_module_proc]

        if self.args.console_control:
            console_parser = Parser.Parser(self.Camera,"console")
            console_parser.start()

        if not self.args.ext_detection:
            self.q = queue.Queue()
            # os.mkfifo("/tmp/rura")
            threading.Thread(target=sender,args=(self.q,), daemon=True).start()

        if self.args.ext_middle_module:
            parser = Parser.Parser(self.Camera,"serial",self.args.ext_middle_module, self.args.duplicate_serial)
        else:
            parser = Parser.Parser(self.Camera,"serial")
        parser.start()

        frame = self.Camera.get_frame()
        self.Streamer.stdin.write(frame.tobytes())
        if self.args.visualize:
    
            self.Player = subprocess.Popen(
                ["ffplay", "-rtsp_transport", "tcp", "rtsp://localhost:8554/live.stream"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self.Subprocesses.append(self.Player)

        self.Drone.start()
        self.Camera.inject_tracked_obj(self.Drone)


    def start(self):
        dt = 1/ 300

        while True:
            dr_x, dr_y = self.Drone.position
            self.Scene.overlay_object(self.Drone)
            frame, offset = self.Camera.get_frame_resolve_drone_offset([int(dr_x) % self.Scene.image_width, int(dr_y)])
            self.Streamer.stdin.write(frame.tobytes())
            if not self.args.ext_detection:
                self.q.put((offset[0], offset[1]))
            # print((offset[0], offset[1]))
            # print([x-y for x,y in zip(cam.orientation, cam.orientation_target) ], cam._resolve_orientation(), offset )
            sleep(dt)

    


sim = Simulation()
sim.init_simulation()
try:
    sim.start()
except KeyboardInterrupt:
    for process in sim.Subprocesses:
        process.kill()
        outs,errs = process.communicate()
    sys.exit()

# proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE,
# stdout=subprocess.DEVNULL,
#  stderr=subprocess.DEVNULL,
# )
# args = InitArgsParser.arg_parser.parse_args()
# scene = Scene.Scene(sim)
# sim.Scene = scene
# cam = Camera.Camera(sim,args.auto_reset)
# cam.start()

# sim.Cam = cam
# print(args)
# if not args.ext_middle_module:
#     serial_emulation = subprocess.Popen(emulate_serial_connection_socat_cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
#     sleep(1)
#     middle_module_proc = subprocess.Popen(["../middle-module/build/main"])

# if args.console_control:
#     console_parser = Parser.Parser(cam,"console")
#     console_parser.start()

# if not args.ext_detection:
#     q = queue.Queue()
#     # os.mkfifo("/tmp/rura")
#     threading.Thread(target=sender,args=(q,), daemon=True).start()
   


# if args.ext_middle_module:
#     parser = Parser.Parser(cam,"serial",args.ext_middle_module)
# else:
#     parser = Parser.Parser(cam,"serial")
# parser.start()

# frame = cam.get_frame()
# proc.stdin.write(frame.tobytes())
# dt = 1/ 300

# drone = Drone.Drone(sim)
# sim.Drone = drone
# drone.start()
# cam.inject_tracked_obj(drone)

# if args.visualize:
    
#     player = subprocess.Popen(
#         ["ffplay", "-rtsp_transport", "tcp", "rtsp://localhost:8554/live.stream"],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL,
#     )




# while True:
#     dr_x, dr_y = drone.position
#     scene.overlay_object(drone)
#     frame, offset = cam.get_frame_resolve_drone_offset([int(dr_x) % scene.image_width, int(dr_y)])
#     proc.stdin.write(frame.tobytes())
#     if not args.ext_detection:
#         q.put((offset[0], offset[1]))
#     # print((offset[0], offset[1]))
#     # print([x-y for x,y in zip(cam.orientation, cam.orientation_target) ], cam._resolve_orientation(), offset )
#     sleep(dt)

# serial_emulation.terminate()
# serial_emulation.wait()
