import threading
import os
import cv2
import numpy as np


class ThreadedCamera:
    """
    Handles video capture in a separate thread for non-blocking I/O.
    """
    def __init__(self, source: str):
        """
        Initializes the camera and starts the reading thread.

        Args:
            source (str): Camera's RTSP URL.
        """
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp'
        self.capture = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.status = False
        self.frame = None
        # To skip frames after inference
        self.frameId = 0

        if self.capture.isOpened():
            self.status, self.frame = self.capture.read()
            self.thread.start()

    def update(self):
        """
        Continuously reads the latest frame from the buffer. 
        Executed in a background thread.
        """
        while True:
            if self.capture.isOpened():
                status, frame = self.capture.read()
                if status:
                    self.status = status
                    self.frame = frame
                    self.frameId += 1
            else:
                break

    def set(self, propId: int, value: float):
        """
        Wraps OpenCV's set method.

        Args:
            propId (int): Property identifier (e.g., cv2.CAP_PROP_FRAME_WIDTH).
            value (float): Value to set.
        """
        self.capture.set(propId, value)

    def get(self, propId: int) -> float:
        """
        Wraps OpenCV's get method.

        Args:
            propId (int): Property identifier.

        Returns:
            float: Value of the property.
        """
        return self.capture.get(propId)

    def read(self) -> tuple[bool, np.ndarray]:
        """
        Returns the most recently captured frame.

        Returns:
            tuple[bool, np.ndarray]: 
                - bool: True if frame is valid, False otherwise.
                - np.ndarray: The image frame (or None if invalid).
        """
        return self.status, self.frame

    def release(self):
        """Releases the video capture resource."""
        self.capture.release()
