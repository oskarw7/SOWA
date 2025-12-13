import threading
import os
import cv2


class ThreadedCamera:
    def __init__(self, source):
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
        self.capture = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.status = False
        self.frame = None
        # Do pomijania klatek po inferencji
        self.frameId = 0

        if self.capture.isOpened():
            self.status, self.frame = self.capture.read()
            self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                status, frame = self.capture.read()
                if status:
                    self.status = status
                    self.frame = frame
                    self.frameId += 1
            else:
                break

    def set(self, propId, value):
        self.capture.set(propId, value)

    def get(self, propId):
        return self.capture.get(propId)

    def read(self):
        return self.status, self.frame

    def release(self):
        self.capture.release()
