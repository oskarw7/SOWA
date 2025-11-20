import cv2
import numpy as np
from detector import Detection


class Vizualizer:
    def __init__(self):
        self.boxColors = [(164, 120, 87), (68, 148, 228), (93, 97, 209), (178, 182, 133), (88, 159, 106),
                       (96, 202, 231), (159, 124, 168), (169, 162, 241), (98, 118, 150), (172, 176, 184)]

    def draw(self, frame: np.ndarray, detections: list[Detection]) -> None:
        for detection in detections:
            color = self.boxColors[detection.classIndex % len(self.boxColors)]
            cv2.rectangle(frame, (detection.xMin, detection.yMin), (detection.xMax, detection.yMax), color, 2)
            label = f'{detection.className}: {int(detection.confidence * 100)}%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            labelYMin = max(detection.yMin, labelSize[1] + 10)
            cv2.rectangle(frame, (detection.xMin, labelYMin - labelSize[1] - 10),
                          (detection.xMin + labelSize[0], labelYMin + baseLine - 10), color,
                          cv2.FILLED)
            cv2.putText(frame, label, (detection.xMin, labelYMin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),
                        1)

    def showFps(self, frame: np.ndarray, fps: float) -> None:
        cv2.putText(frame, f'FPS: {fps:0.2f}', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (51, 255, 51), 2)

