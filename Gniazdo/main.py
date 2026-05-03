import queue
import subprocess
import threading
from time import sleep, time

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
        self.Cam =None
        self.Scene =None
        self.Drone =None
        self.Parser = None
    


sim = Simulation()

proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE,
stdout=subprocess.DEVNULL,
 stderr=subprocess.DEVNULL,
)
args = InitArgsParser.arg_parser.parse_args()
scene = Scene.Scene(sim)
sim.Scene = scene
cam = Camera.Camera(sim,args.auto_reset)
cam.start()

sim.Cam = cam
print(args)
if not args.ext_middle_module:
    serial_emulation = subprocess.Popen(emulate_serial_connection_socat_cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    sleep(1)
    middle_module_proc = subprocess.Popen(["../middle-module/build/main"])

if args.console_control:
    console_parser = Parser.Parser(cam,"console")
    console_parser.start()

if not args.ext_detection:
    q = queue.Queue()
    # os.mkfifo("/tmp/rura")
    threading.Thread(target=sender,args=(q,), daemon=True).start()
   


if args.ext_middle_module:
    parser = Parser.Parser(cam,"serial",args.ext_middle_module)
else:
    parser = Parser.Parser(cam,"serial")
parser.start()

frame = cam.get_frame()
proc.stdin.write(frame.tobytes())
dt = 1/ 300

drone = Drone.Drone(sim)
sim.Drone = drone
drone.start()
cam.inject_tracked_obj(drone)

if args.visualize:
    
    player = subprocess.Popen(
        ["ffplay", "-rtsp_transport", "tcp", "rtsp://localhost:8554/live.stream"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )




while True:
    dr_x, dr_y = drone.position
    scene.overlay_object(drone)
    frame, offset = cam.get_frame_resolve_drone_offset([int(dr_x) % scene.image_width, int(dr_y)])
    proc.stdin.write(frame.tobytes())
    if not args.ext_detection:
        q.put((offset[0], offset[1]))
    # print((offset[0], offset[1]))
    # print([x-y for x,y in zip(cam.orientation, cam.orientation_target) ], cam._resolve_orientation(), offset )
    sleep(dt)

serial_emulation.terminate()
serial_emulation.wait()
