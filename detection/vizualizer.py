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
            cv2.rectangle(frame, (detection.minX, detection.minY), (detection.maxX, detection.maxY), color, 2)

            # Wizualizacja offsetow
            cv2.line(frame, (detection.centerX, detection.centerY), (int(w/2), int(h/2)), color, 1)
            label = f'{detection.className}: {int(detection.confidence * 100)}% Off:({detection.offsetX}, {detection.offsetY})'

            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            labelMinY = max(detection.minY, labelSize[1] + 10)
            cv2.rectangle(frame, (detection.minX, labelMinY - labelSize[1] - 10),
                          (detection.minX + labelSize[0], labelMinY + baseLine - 10), color,
                          cv2.FILLED)
            cv2.putText(frame, label, (detection.minX, labelMinY - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0),
                        1)

    def drawGrid(self, frame: np.ndarray, tileSize: int, overlap: float) -> None:
        """
        Draws the boundaries of the inference tiles with a thin line.
        """
        imgH, imgW = frame.shape[:2]
        step = int(tileSize * (1 - overlap))
        gridColor = (255, 255, 255)

        for y in range(0, imgH, step):
            for x in range(0, imgW, step):
                startX = min(x, imgW - tileSize)
                startY = min(y, imgH - tileSize)
                startX = max(0, startX)
                startY = max(0, startY)

                cv2.rectangle(frame, (startX, startY), (startX + tileSize, startY + tileSize), gridColor, 1)

                if startX + tileSize >= imgW:
                    break
            if startY + tileSize >= imgH:
                break

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
