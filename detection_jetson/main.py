import argparse
import time
# import numpy as np
# from datetime import datetime

from detector import Detector
from camera import ThreadedCamera

parser = argparse.ArgumentParser()
parser.add_argument('--model', help='Path to YOLO model file (example: "runs/detect/train/weights/best.pt")',
                    required=True)
parser.add_argument('--conf', help='Minimum confidence threshold for displaying detected objects (example: "0.4")',
                    default=0.5)
parser.add_argument('--overlap', help='Defines how much tiles should interfere in tiled detection (example: "0.1")',
                    default=0.1)
parser.add_argument('--tile', help='Defines size of an inference tile (example: "640")',
                    default=640)
args = parser.parse_args()

MODEL_PATH = args.model
CONFIDENCE_THRESHOLD = args.conf
OVERLAP = args.overlap
TILE_SIZE = args.tile
SOURCE = 'rtsp://admin:admin1234@192.168.5.190:554/main'

cap = ThreadedCamera(SOURCE)

detector = Detector(MODEL_PATH, CONFIDENCE_THRESHOLD, overlap=OVERLAP, tileSize=TILE_SIZE)

prev_frame_id = -1
# INFO: FPS counter stays in the code if debug is needed during system tests
# fpsMA = 0.0  # Moving Average
# fpsMABuffer = []
# fpsMAThreshold = 30
# imageCount = 0
# times = []
try:
    while True:
        # startTime = time.perf_counter()

        ret, frame = cap.read()

        # TODO: Check if second condition below is enough, if not bring back first one
        # if hasattr(cap, 'frame_id'):
            # if cap.frameId == prev_frame_id:
                # time.sleep(0.005)
                # continue

        if not ret or frame is None:
            continue

        # inferenceStartTime = time.perf_counter()

        # results = detector.detectTiledBatch(frame)
        results = detector.detect(frame)

        # TODO: API pass
        # ------ PLACE FOR API PASS -----
        # INFO: Access offsets from the center like: result.offsetX, result.offsetY

        # endTime = time.perf_counter()
        # times.append(endTime - inferenceStartTime)
        # fpsCurrent = 1 / (endTime - startTime)
        # if len(fpsMABuffer) >= fpsMAThreshold:
            # fpsMABuffer.pop(0)
        # fpsMABuffer.append(fpsCurrent)
        # fpsMA = float(np.mean(fpsMABuffer))
        # print(f'Frame capture and inference time: {(endTime - startTime)*1000} ms')

except KeyboardInterrupt:
    print("\nStopping the process...")

finally:
    cap.release()
    print("\nResources freed. Program ends.")
