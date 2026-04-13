import cv2
import numpy as np
import subprocess
from Camera import Camera
from Scene import Scene 
from Drone import Drone
from time import sleep
import threading


def handle_command(cam, cmd):
    parts = cmd.strip().lower().split()

    i = 0
    while i < len(parts):
        direction = parts[i]

        if i + 1 < len(parts) and parts[i + 1].isdigit():
            value = int(parts[i + 1])
            i += 2
        else:
            value = 1
            i += 1

        if direction == "up":
            cam.move_vertical( -1 * value)
        elif direction == "down":
            cam.move_vertical(value)
        elif direction == "left":
            cam.move_horizontal(-1 * value)
        elif direction == "right":
            cam.move_horizontal(value)
        elif direction == "stop":
            with cam.lock():
                cam.orientation_target =  cam.orientation
        else:
            print(f"Unknown command: {direction}")

def input_thread(camera):
    while True:
        cmd = input()
        handle_command(cam,cmd)
       



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


scene = Scene.Scene()
cam = Camera.Camera(scene)
cam.start()
threading.Thread(target=input_thread, args=(cam,), daemon=True).start()
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


