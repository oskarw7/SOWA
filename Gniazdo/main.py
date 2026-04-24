import queue
import subprocess
import threading
from time import sleep, time

import cv2
import numpy as np
from Camera import Camera
from Drone import Drone
from Parser import Parser
from Scene import Scene

q = queue.Queue()


def sender():
    with open("/tmp/rura", "w") as rura:
        with q.mutex:
            q.queue.clear()
        while True:
            x, y = q.get()
            print(int(x), int(y))
            if x != -1:
                rura.write(f"{int(x)} {int(y)}\n")
                rura.flush()


threading.Thread(target=sender, daemon=True).start()


width, height = 1920, 1080
fps = 24

ffmpeg_cmd = [
    "ffmpeg",
    "-re",
    "-f",
    "rawvideo",
    "-pix_fmt",
    "bgr24",
    "-s",
    f"{width}x{height}",
    "-r",
    str(fps),
    "-i",
    "-",
    "-vf",
    "format=yuv420p",  # stdin
    "-c:v",
    "libx264",
    "-preset",
    "ultrafast",
    "-tune",
    "zerolatency",
    "-f",
    "rtsp",
    "-rtsp_transport",
    "tcp",
    "rtsp://localhost:8554/live.stream",
]

proc = subprocess.Popen(
    ffmpeg_cmd,
    stdin=subprocess.PIPE,
    # stdout=subprocess.DEVNULL,
    # stderr=subprocess.DEVNULL,
)


serial_emulation = subprocess.Popen(
    [
        "socat",
        "-x",
        "PTY,link=/tmp/virt,raw",
        "PTY,link=/tmp/virt2,raw",
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

scene = Scene.Scene()
cam = Camera.Camera(scene)
cam.start()

# parser = Parser.Parser(cam)
parser = Parser.Parser(cam, "serial")
parser.start()

frame = cam.get_frame()
x = 0
dt = 1 / 300

drone = Drone.Drone()
drone.start()

cv2.imwrite("test.jpg", drone.image)
proc3 = subprocess.Popen(
    ["ffplay", "-rtsp_transport", "tcp", "rtsp://localhost:8554/live.stream"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

cntr = 0

while True:
    timestamp = time()
    x += 1
    with drone.lock:
        dr_x, dr_y = drone.position
    isInFrame = scene.overlay_image(drone.image, int(dr_x), int(dr_y))

    frame, offset = cam.get_frame_resolve_drone_offset([int(dr_x), int(dr_y)])
    frame[1080 // 2 : 1080 // 2 + 100, 1920 // 2 : 1920 // 2 + 100] = np.zeros(
        (100, 100, 3), np.uint8
    ).copy()
    proc.stdin.write(frame.tobytes())
    q.put((offset[0], offset[1]))
    sleep(dt)
    print(f"current fps = {1 / (time() - timestamp)}")


serial_emulation.terminate()
serial_emulation.wait()
