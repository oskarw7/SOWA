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
    "-",  # stdin
    "-vf",
    "format=yuv420p",
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

emulate_serial_connection_socat_cmd = [
    "socat",
    "-d",
    "-d",
    "-x",
    "PTY,link=/tmp/virt,raw",
    "PTY,link=/tmp/virt2,raw",
]


def sender(q):
    with open("/tmp/rura", "w") as rura:
        with q.mutex:
            q.queue.clear()
        while True:
            x, y = q.get()
            # print(x,y,"wysylam")
            if x != -1:
                rura.write(f"{int(x)} {int(y)}\n")
                rura.flush()
