import argparse
import glob
import os
import sys
import time
from datetime import datetime

import cv2
import numpy as np

from detector import Detector
from vizualizer import Vizualizer
from camera import ThreadedCamera

parser = argparse.ArgumentParser()
parser.add_argument('--model', help='Path to YOLO model file (example: "runs/detect/train/weights/best.pt")',
                    required=True)
parser.add_argument('--source', help='Image source, can be image file ("test.jpg"), \
                    image folder ("test_dir"), video file ("testvid.mp4") or camera ("camera")',
                    required=True)
parser.add_argument('--thresh', help='Minimum confidence threshold for displaying detected objects (example: "0.4")',
                    default=0.5)
parser.add_argument('--resolution', help='Resolution in WxH to display inference results at (example: "640x480"), \
                    otherwise, match source resolution',
                    default=None)
parser.add_argument('--record', help='Add this flag to save detection results as MP4 file. Works only for video and camera sources.', action='store_true')
parser.add_argument('--device', help='Device to run inference on (example: "0" for GPU, "cpu" for CPU)', default='0')
parser.add_argument('--headless', action=argparse.BooleanOptionalAction)
args = parser.parse_args()

MODEL_PATH = args.model
SOURCE = args.source
CONFIDENCE_THRESHOLD = args.thresh
RESOLUTION = args.resolution
RECORD_FLAG = args.record
DEVICE = args.device
HEADLESS = args.headless

IMAGE_EXTENSIONS = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.bmp', '.BMP']
VIDEO_EXTENSIONS = ['.avi', '.mov', '.mp4', '.mkv', '.wmv']


if os.path.isdir(SOURCE):
    sourceType = 'folder'
elif os.path.isfile(SOURCE):
    _, ext = os.path.splitext(SOURCE)
    if ext in IMAGE_EXTENSIONS:
        sourceType = 'image'
    elif ext in VIDEO_EXTENSIONS:
        sourceType = 'video'
    else:
        print(f'File extension {ext} is not supported.')
        sys.exit(0)
elif SOURCE == 'camera':
    SOURCE = 'rtsp://admin:admin1234@192.168.5.190:554/main'
    sourceType = 'camera'
else:
    print(f'Input {SOURCE} is invalid. Please try again.')
    sys.exit(0)

if RESOLUTION:
    resWidth, resHeight = int(RESOLUTION.split('x')[0]), int(RESOLUTION.split('x')[1])

if sourceType == 'image':
    imageList = [SOURCE]
elif sourceType == 'folder':
    imageList = []
    fileList = glob.glob(SOURCE + '/*')
    for file in fileList:
        _, fileExt = os.path.splitext(file)
        if fileExt in IMAGE_EXTENSIONS:
            imageList.append(file)
elif sourceType == 'video' or sourceType == 'camera':
    if sourceType == 'video':
        cap = cv2.VideoCapture(SOURCE)
    else:
        cap = ThreadedCamera(SOURCE)
    if RESOLUTION:
        _ = cap.set(cv2.CAP_PROP_FRAME_WIDTH, resWidth)
        _ = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resHeight)

    if RECORD_FLAG:
        if not RESOLUTION:
            print('Resolution not provided. Recording is not possible.')
            sys.exit(1)
        os.makedirs('saved_videos', exist_ok=True)
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        videoName = os.path.join('saved_videos', f'video_{timestamp}.mp4')
        videoRecorder = cv2.VideoWriter(videoName, cv2.VideoWriter_fourcc(*'mp4v'), 30, (resWidth, resHeight))

if not HEADLESS:
    windowName = 'Detection results'
    cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(windowName, 1920, 1080)

detector = Detector(MODEL_PATH, CONFIDENCE_THRESHOLD, device=DEVICE)
vizualizer = Vizualizer()

prev_frame_id = -1
fpsMA = 0.0  # Moving Average zeby wygladzic
fpsMABuffer = []
fpsMAThreshold = 30
imageCount = 0
times = []
while True:
    startTime = time.perf_counter()

    if sourceType == 'image' or sourceType == 'folder':
        if imageCount >= len(imageList):
            print('All images have been processed. Exiting program.')
            break
        imgFilename = imageList[imageCount]
        frame = cv2.imread(imgFilename)
        imageCount += 1

    elif sourceType == 'video' or sourceType == 'camera':
        ret, frame = cap.read()

        if sourceType == 'camera':
            if hasattr(cap, 'frame_id'):
                if cap.frameId == prev_frame_id:
                    time.sleep(0.005)
                    continue

        if not ret:
            if sourceType == 'video':
                print('Reached end of the video file. Exiting program.')
            else:
                print('Error occurred while capturing frame')
            break

    if RESOLUTION:
        frame = cv2.resize(frame, (resWidth, resHeight))

    inferenceStartTime = time.perf_counter()

    # results = detector.detectTiledBatch(frame, tileSize=640, overlap=0.1)
    results = detector.detectBatch(frame)


    endTime = time.perf_counter()
    times.append(endTime - inferenceStartTime)
    fpsCurrent = 1 / (endTime - startTime)
    if len(fpsMABuffer) >= fpsMAThreshold:
        fpsMABuffer.pop(0)
    fpsMABuffer.append(fpsCurrent)
    fpsMA = float(np.mean(fpsMABuffer))
    print(f'Frame capture and inference time: {(endTime - startTime)*1000} ms')

    vizualizer.draw(frame, results)
    # vizualizer.drawGrid(
            # frame,
            # tileSize=640,
            # overlap=0.0)
    if not HEADLESS:
        if sourceType == 'video' or sourceType == 'camera':
            vizualizer.showFps(frame, fpsMA)
        cv2.imshow(windowName, frame)

    if RECORD_FLAG and (sourceType == 'video' or sourceType == 'camera'):
        videoRecorder.write(frame)

    if sourceType == 'image' or sourceType == 'folder':
        key = cv2.waitKey()
    elif sourceType == 'video' or sourceType == 'camera':
        key = cv2.waitKey(1)
    if key == ord('q') or key == ord('Q') or key == 27:
        break
    elif key == ord('p') or key == ord('P'):  # pause
        cv2.waitKey()
    elif key == ord('s') or key == ord('S'):  # save
        os.makedirs('saved_frames', exist_ok=True)
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        filename = os.path.join('saved_frames', f'frame_{timestamp}.png')
        cv2.imwrite(filename, frame)

'''
if sourceType == 'video' or 'folder':
    vizualizer.plotBenchmark(times, SOURCE)
elif sourceType == 'camera':
    vizualizer.plotBenchmark(times, sourceType)
'''

if sourceType == 'video' or sourceType == 'camera':
    cap.release()
    if RECORD_FLAG:
        videoRecorder.release()
cv2.destroyAllWindows()
