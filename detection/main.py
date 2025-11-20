import argparse
import glob
import os
import sys
from datetime import datetime

import cv2

from detector import Detector
from vizualiser import Vizualiser

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
args = parser.parse_args()

MODEL_PATH = args.model
SOURCE = args.source
CONFIDENCE_THRESHOLD = args.thresh
RESOLUTION = args.resolution

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
    # INFO: do sprawdzenia, bylo w pierwotnym kodzie z RPI4; URL podawany w kodzie dla wygody
    # os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS']='rtsp_transport;tcp'
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
        cap = cv2.VideoCapture(SOURCE, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            print(f'RTSP stream {SOURCE} could not be opened.')
            sys.exit(0)
    if RESOLUTION:
        _ = cap.set(cv2.CAP_PROP_FRAME_WIDTH, resWidth)
        _ = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resHeight)

detector = Detector(MODEL_PATH, CONFIDENCE_THRESHOLD)
vizualiser = Vizualiser(sourceType)
imageCount = 0
while True:
    if sourceType == 'image' or sourceType == 'folder':
        if imageCount >= len(imageList):
            print('All images have been processed. Exiting program.')
            break
        imgFilename = imageList[imageCount]
        frame = cv2.imread(imgFilename)
        imageCount += 1

    elif sourceType == 'video' or sourceType == 'camera':
        ret, frame = cap.read()
        if not ret:
            if sourceType == 'video':
                print('Reached end of the video file. Exiting program.')
            else:
                print('Error occurred while capturing frame')
            break

    if RESOLUTION:
        frame = cv2.resize(frame, (resWidth, resHeight))

    results = detector.detect(frame)
    vizualiser.draw(frame, results)

    if sourceType == 'image' or sourceType == 'folder':
        key = cv2.waitKey()
    elif sourceType == 'video' or sourceType == 'camera':
        key = cv2.waitKey(5)
    if key == ord('q') or key == ord('Q') or key == 27:
        break
    elif key == ord('p') or key == ord('P'): # pause
        cv2.waitKey()
    elif key == ord('s') or key == ord('S'): # save
        os.makedirs('saved_frames', exist_ok=True)
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        filename = os.path.join('saved_frames', f'frame_{timestamp}.png')
        cv2.imwrite(filename, frame)

if sourceType == 'video' or sourceType == 'camera':
    cap.release()
cv2.destroyAllWindows()