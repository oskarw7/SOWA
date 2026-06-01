import paramiko


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
    "PTY,link=/tmp/virt,raw,echo=0",
    "PTY,link=/tmp/virt2,raw,echo=0",
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

class SSHManager:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.client.connect(
            hostname=self.host,
            username=self.username,
            password=self.password,
            timeout=10
        )

    def run_commands(self):
        commands = [
            "cd /home/sowa/SOWA/detection_jetson/DeepStream-Yolo && nohup just run > deepstream.log 2>&1 &",
            "cd /home/sowa/SOWA/mujfolder && nohup sudo -S make run > make.log 2>&1 &"
        ]

        for cmd in commands:
            stdin, stdout, stderr = self.client.exec_command(cmd)

            # if sudo needs password:
            if "sudo" in cmd:
                stdin.write(self.password + "\n")
                stdin.flush()

    def close(self):
        if self.client:
            self.client.close()