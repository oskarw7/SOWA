import os
from datetime import datetime
import cv2
import numpy as np
import matplotlib.pyplot as plt
from detector import Detection


class Vizualizer:
    def __init__(self):
        self.boxColors = [(164, 120, 87), (68, 148, 228), (93, 97, 209), (178, 182, 133), (88, 159, 106),
                          (96, 202, 231), (159, 124, 168), (169, 162, 241), (98, 118, 150), (172, 176, 184)]

    def draw(self, frame: np.ndarray, detections: list[Detection]) -> None:
        h, w = frame.shape[:2]
        cv2.circle(frame, (int(w/2), int(h/2)), 5, (0, 0, 255), -1)  # Draw center of image

        for detection in detections:
            color = self.boxColors[detection.classIndex % len(self.boxColors)]
            cv2.rectangle(frame, (detection.xMin, detection.yMin), (detection.xMax, detection.yMax), color, 2)

            # Wizualizacja offsetow
            cv2.line(frame, (detection.centerX, detection.centerY), (int(w/2), int(h/2)), color, 1)
            label = f'{detection.className}: {int(detection.confidence * 100)}% Off:({detection.offsetX}, {detection.offsetY})'

            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            labelYMin = max(detection.yMin, labelSize[1] + 10)
            cv2.rectangle(frame, (detection.xMin, labelYMin - labelSize[1] - 10),
                          (detection.xMin + labelSize[0], labelYMin + baseLine - 10), color,
                          cv2.FILLED)
            cv2.putText(frame, label, (detection.xMin, labelYMin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),
                        1)

    def showFps(self, frame: np.ndarray, fps: float) -> None:
        cv2.putText(frame, f'FPS: {fps:0.2f}', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (51, 255, 51), 2)

    def plotBenchmark(self, times: list[float], source: str, device: str = 'GPU') -> None:
        times = [t*1000 for t in times]
        plt.plot(times[1:])  # pominiecie pierwszego pomiaru ze wzgledu na za duzy odchyl (0.7 vs 10^{-2})
        plt.xlabel('Frame index')
        plt.ylabel('Time [ms]')
        plt.title(f'Inference time for {source} on {device}')
        os.makedirs('benchmark_plots', exist_ok=True)
        timestamp = datetime.now().strftime('%d%m%Y_%H%M%S')
        filename = os.path.join('benchmark_plots', f'plot_{device}_{timestamp}.png')
        plt.savefig(filename)
        plt.close()
