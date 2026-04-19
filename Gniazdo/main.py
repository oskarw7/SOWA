import cv2
import numpy as np
import subprocess
from Camera import Camera
from Scene import Scene 
from Drone import Drone
from time import sleep
import threading
from Parser import Parser




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

proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

serial_emulation = subprocess.Popen(["socat",
    "-d", "-d", "-v", "-x",
    "PTY,link=/tmp/virt,raw,echo=0",
    "PTY,link=/tmp/virt2,raw,echo=0"
,])

scene = Scene.Scene()
cam = Camera.Camera(scene)
cam.start()

parser = Parser.Parser(cam,"serial")
parser.start()

frame = cam.get_frame()
x=0
dt = 1/ 300

drone = Drone.Drone() 
drone.start()

cv2.imwrite("test.jpg",drone.image)

while True:

    x+=1
    frame = cam.get_frame()
    with drone.lock:
    
        dr_x , dr_y = drone.position
    scene.overlay_image(drone.image, int(dr_x) , int(dr_y))
    proc.stdin.write(frame.tobytes())
    

    sleep(dt)


serial_emulation.terminate()
serial_emulation.wait()