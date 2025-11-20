from ultralytics import YOLO
import numpy as np


class Detection:
    def __init__(self, xMin: int, yMin: int, xMax: int, yMax: int, confidence: float, className: str, classIndex: int):
        self.xMin = xMin
        self.yMin = yMin
        self.xMax = xMax
        self.yMax = yMax
        self.confidence = confidence
        self.className = className
        self.classIndex = classIndex

class Detector:
    def __init__(self, modelPath: str, confidenceThreshold: float):
        self.model = YOLO(modelPath, task='detect')
        self.labels = self.model.names
        self.confidenceThreshold = confidenceThreshold

    def detect(self, frame: np.ndarray) -> list[Detection]:
        interferenceResults = self.model(frame, verbose=False)
        detections = interferenceResults[0].boxes
        finalResults = []
        for i in range(len(detections)):
            coords = detections[i].xyxy.cpu().numpy().squeeze()
            xMin, yMin, xMax, yMax = coords.astype(int)
            classIndex = int(detections[i].cls.item())
            className = self.labels[classIndex]
            confidence = detections[i].conf.item()
            if confidence >= self.confidenceThreshold:
                finalResults.append(Detection(xMin, yMin, xMax, yMax, confidence, className, classIndex))
        return finalResults
