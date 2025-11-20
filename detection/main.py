import argparse
import glob
import os
import sys

import cv2

from detector import Detector
from vizualiser import Vizualiser

parser = argparse.ArgumentParser()
parser.add_argument('--model', help='Path to YOLO model file (example: "runs/detect/train/weights/best.pt")',
                    required=True)
parser.add_argument('--source', help='Image source, can be image file ("test.jpg"), \
                    image folder ("test_dir"), video file ("testvid.mp4")',
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
else:
    print(f'Input {SOURCE} is invalid. Please try again.')
    sys.exit(0)

resize = False
if RESOLUTION:
    resize = True
    resW, resH = int(RESOLUTION.split('x')[0]), int(RESOLUTION.split('x')[1])

if sourceType == 'image':
    imageList = [SOURCE]
elif sourceType == 'folder':
    imageList = []
    fileList = glob.glob(SOURCE + '/*')
    for file in fileList:
        _, fileExt = os.path.splitext(file)
        if fileExt in IMAGE_EXTENSIONS:
            imageList.append(file)
elif sourceType == 'video':
    cap = cv2.VideoCapture(SOURCE)
    if RESOLUTION:
        _ = cap.set(3, resW)
        _ = cap.set(4, resH)

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

    elif sourceType == 'video':
        ret, frame = cap.read()
        if not ret:
            print('Reached end of the video file. Exiting program.')
            break

    if resize:
        frame = cv2.resize(frame,(resW,resH))

    results = detector.detect(frame)
    vizualiser.draw(frame, results)

    if sourceType == 'image' or sourceType == 'folder':
        key = cv2.waitKey()
    elif sourceType == 'video':
        key = cv2.waitKey(5)
    if key == ord('q') or key == ord('Q') or key == 27:
        break
    elif key == ord('p') or key == ord('P'):
        cv2.waitKey()
    elif key == ord('s') or key == ord('S'):
        cv2.imwrite('saved_frame.png', frame)

if sourceType == 'video':
    cap.release()
cv2.destroyAllWindows()