import cv2
import numpy as np
import subprocess
from Camera import Camera
from Scene import Scene 
from Drone import Drone
from time import sleep
import threading
from Parser import Parser
import os
import queue

q = queue.Queue()


def sender():
    with open("/tmp/rura", "w") as rura:
        with q.mutex:
            q.queue.clear()
        while True:
            x, y = q.get()
            print(x,y)
            if x != -1:
                rura.write(f"{int(x)} {int(y)}\n")
                rura.flush()

threading.Thread(target=sender, daemon=True).start()


width, height = 1920, 1080
fps = 24

ffmpeg_cmd = [
    "ffmpeg",
    "-re",
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-s", f"{width}x{height}",
    "-r", str(fps),
    "-i", "-",  # stdin
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-tune", "zerolatency",
    "-f", "rtsp",
    "-rtsp_transport", "tcp",
    "rtsp://localhost:8554/live.stream"
]

proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE,
stdout=subprocess.DEVNULL,
 stderr=subprocess.DEVNULL)



serial_emulation = subprocess.Popen(["socat",
    "-d", "-d", "-x",
    "PTY,link=/tmp/virt,raw,echo=0",
    "PTY,link=/tmp/virt2,raw,echo=0"
,])

scene = Scene.Scene()
cam = Camera.Camera(scene)
cam.start()

# parser = Parser.Parser(cam)
parser = Parser.Parser(cam,"serial")
parser.start()

frame = cam.get_frame()
x=0
dt = 1/ 300

drone = Drone.Drone() 
drone.start()

cv2.imwrite("test.jpg",drone.image)
proc3 = subprocess.Popen([
    "ffplay",
    "-rtsp_transport", "tcp",
    "rtsp://localhost:8554/live.stream"
],
stdout=subprocess.DEVNULL,
stderr=subprocess.DEVNULL
)

while True:
    x+=1
    with drone.lock:
    
        dr_x , dr_y = drone.position
    isInFrame = scene.overlay_image(drone.image, int(dr_x) , int(dr_y))

    frame, offset = cam.get_frame_resolve_drone_offset([int(dr_x),int(dr_y)])
    proc.stdin.write(frame.tobytes())
    q.put((offset[0],offset[1]))
    sleep(dt)



serial_emulation.terminate()
serial_emulation.wait()