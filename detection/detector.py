from ultralytics import YOLO
import numpy as np
import cv2


class Detection:
    def __init__(self, minX: int, minY: int, maxX: int, maxY: int, confidence: float, className: str, classIndex: int, frameW: int, frameH: int):
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY
        self.confidence = confidence
        self.className = className
        self.classIndex = classIndex

        # --- Center and Offset Calculation ---
        self.centerX = int((minX + maxX) / 2)
        self.centerY = int((minY + maxY) / 2)

        imageCenterX = int(frameW / 2)
        imageCenterY = int(frameH / 2)

        # Offset: (Negative = Left/Up, Positive = Right/Down from center)
        self.offsetX = self.centerX - imageCenterX
        self.offsetY = self.centerY - imageCenterY


class Detector:
    def __init__(self, modelPath: str, confidenceThreshold: float, device: str = '0', classes=None):
        # Default '0' for GPU
        self.device = device
        self.model = YOLO(modelPath, task='detect')
        self.labels = self.model.names
        self.confidenceThreshold = confidenceThreshold
        # Default [4, 8] sets only airplanes and boats to be detected
        if classes is None:
            classes = [4, 8]
        self.classes = classes

    def detect(self, frame: np.ndarray) -> list[Detection]:
        # Pass device to the model
        return self._processResults(self.model(frame, device=self.device, verbose=False, classes=self.classes)[0], frame.shape, offset=(0, 0))

    def detectTiled(self, frame: np.ndarray, tileSize: int = 640, overlap: float = 0.25) -> list[Detection]:
        """
        Splits image into tiles, detects, maps coordinates back, and removes duplicates.
        """
        imgH, imgW = frame.shape[:2]
        step = int(tileSize * (1 - overlap))

        allDetections = []

        # Generate tiles
        for y in range(0, imgH, step):
            for x in range(0, imgW, step):
                startX = min(x, imgW - tileSize)
                startY = min(y, imgH - tileSize)

                startX = max(0, startX)
                startY = max(0, startY)

                crop = frame[startY:startY + tileSize, startX:startX + tileSize]

                # Pass the device to the model
                results = self.model(crop, device=self.device, verbose=False, classes=self.classes, imgsz=tileSize)

                tileDetections = self._processResults(results[0], frame.shape, offset=(startX, startY))
                allDetections.extend(tileDetections)

                if startX + tileSize >= imgW:
                    break
            if startY + tileSize >= imgH:
                break

        return self._applyNms(allDetections)

    def _processResults(self, result, frameShape, offset: tuple) -> list[Detection]:
        detectionsList = []
        boxes = result.boxes
        offX, offY = offset
        frameH, frameW = frameShape[:2]

        for i in range(len(boxes)):
            confidence = boxes[i].conf.item()
            if confidence >= self.confidenceThreshold:
                coords = boxes[i].xyxy.cpu().numpy().squeeze()
                xMin, yMin, xMax, yMax = coords.astype(int)

                xMin += offX
                yMin += offY
                xMax += offX
                yMax += offY

                classIndex = int(boxes[i].cls.item())
                className = self.labels[classIndex]

                detectionsList.append(Detection(xMin, yMin, xMax, yMax, confidence, className, classIndex, frameW, frameH))

        return detectionsList

    def _applyNms(self, detections: list[Detection], iouThresh: float = 0.45) -> list[Detection]:
        if not detections:
            return []

        boxes = []
        scores = []

        for det in detections:
            w = det.maxX - det.minX
            h = det.maxY - det.minY
            boxes.append([det.minX, det.minY, w, h])
            scores.append(det.confidence)

        indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidenceThreshold, iouThresh)

        finalDetections = []
        if len(indices) > 0:
            for i in indices.flatten():
                finalDetections.append(detections[i])

        return finalDetections
