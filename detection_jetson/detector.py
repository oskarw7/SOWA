from ultralytics import YOLO
import numpy as np
import cv2


class Detection:
    """
    Data class representing a single detected object.
    """

    def __init__(self, minX: int, minY: int, maxX: int, maxY: int, confidence: float, className: str, classIndex: int, frameW: int, frameH: int):
        """
        Initializes a Detection object with calculated centers and offsets.

        Args:
            minX (int): Top-left X coordinate.
            minY (int): Top-left Y coordinate.
            maxX (int): Bottom-right X coordinate.
            maxY (int): Bottom-right Y coordinate.
            confidence (float): Confidence score of the detection.
            className (str): Label of the detected class.
            classIndex (int): Index ID of the detected class.
            frameW (int): Width of the entire frame (for offset calc).
            frameH (int): Height of the entire frame (for offset calc).
        """
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
    """
    Wrapper class for YOLO model inference, supporting standard and tiled detection.
    """

    def __init__(self, modelPath: str, confidenceThreshold: float, iouThreshold: float = 0.45, overlap: float = 0.1, tileSize: int = 640, batchSize: int = 8, device: str = '0', precision: str = 'fp16', classes: list[int] = None):
        """
        Initializes the YOLO detector.

        Args:
            modelPath (str): File path to the .pt YOLO model.
            confidenceThreshold (float): Minimum confidence (0-1) to accept detection.
            device (str, optional): Computation device ('0', 'cpu', 'mps'). Defaults to '0'.
            classes (list[int], optional): List of class IDs to detect. If None, defaults to [4, 8] (airplanes and boats).
        """
        self.model = YOLO(modelPath, task='detect')
        self.labels = self.model.names
        self.confidenceThreshold = confidenceThreshold
        self.iouThreshold = iouThreshold
        self.overlap = overlap
        self.tileSize = tileSize
        self.batchSize = batchSize
        self.device = device
        if precision == 'fp16': self.half = True
        else: self.half = False
        if classes is None:
            classes = [4, 8]
        self.classes = classes

    def detect(self, frame: np.ndarray) -> list[Detection]:
        """
        Performs standard inference on the whole frame.

        Args:
            frame (np.ndarray): Input image in BGR format (OpenCV).

        Returns:
            list[Detection]: A list of Detection objects found in the frame.
        """
        # Pass the device to the model
        return self._processResults(
            self.model(
                frame, 
                device=self.device, 
                verbose=False, 
                half=self.half, 
                classes=self.classes
            )[0], 
            frame.shape, 
            offset=(0, 0)
        )

    def detectTiled(self, frame: np.ndarray) -> list[Detection]:
        """
        Splits image into tiles, detects objects, and merges results using NMS.

        Args:
            frame (np.ndarray): Input high-resolution image.
            overlap (float, optional): Overlap ratio between tiles (0.0 to 1.0). Defaults to 0.25.

        Returns:
            list[Detection]: Consolidated list of unique detections after NMS.
        """
        imgH, imgW = frame.shape[:2]
        step = int(self.tileSize * (1 - self.overlap))

        allDetections = []

        # Generate tiles
        for y in range(0, imgH, step):
            for x in range(0, imgW, step):
                startX = min(x, imgW - self.tileSize)
                startY = min(y, imgH - self.tileSize)

                startX = max(0, startX)
                startY = max(0, startY)

                crop = frame[startY:startY + self.tileSize, startX:startX + self.tileSize]

                # Pass the device to the model
                results = self.model(
                    crop, 
                    device=self.device, 
                    verbose=False, 
                    half=self.half, 
                    classes=self.classes, 
                    imgsz=self.tileSize
                )

                tileDetections = self._processResults(results[0], frame.shape, offset=(startX, startY))
                allDetections.extend(tileDetections)

                if startX + self.tileSize >= imgW:
                    break
            if startY + self.tileSize >= imgH:
                break

        return self._applyNms(allDetections)

    def detectTiledBatch(self, frame: np.ndarray) -> list[Detection]:
        imgH, imgW = frame.shape[:2]
        step = int(self.tileSize * (1 - self.overlap))

        allDetections = []
        crops = []
        offsets = []

        for y in range(0, imgH, step):
            for x in range(0, imgW, step):
                startX = min(x, imgW - self.tileSize)
                startY = min(y, imgH - self.tileSize)

                startX = max(0, startX)
                startY = max(0, startY)

                crop = frame[startY:startY + self.tileSize, startX:startX + self.tileSize]
                
                crops.append(crop)
                offsets.append((startX, startY))

                if startX + self.tileSize >= imgW:
                    break
            if startY + self.tileSize >= imgH:
                break

        if crops:
            for i in range(0, len(crops), self.batchSize):
                batchCrops = crops[i:i + self.batchSize]
                batchOffsets = offsets[i:i + self.batchSize]

                results = self.model(
                    batchCrops, 
                    device=self.device, 
                    verbose=False, 
                    half=self.half,
                    classes=self.classes, 
                    imgsz=self.tileSize, 
                    stream=True
                )

                for result, offset in zip(results, batchOffsets):
                    tileDetections = self._processResults(result, frame.shape, offset=offset)
                    allDetections.extend(tileDetections)

        return self._applyNms(allDetections)

    def _processResults(self, result, frameShape, offset: tuple) -> list[Detection]:
        """
        Internal method to convert YOLO raw results to Detection objects.

        Args:
            result: The raw result object from ultralytics YOLO.
            frameShape (tuple): Shape of the full original frame (H, W, C).
            offset (tuple): (x_offset, y_offset) of the current tile.

        Returns:
            list[Detection]: List of formatted Detection objects with global coordinates.
        """
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

                detectionsList.append(
                    Detection(xMin, yMin, xMax, yMax, confidence, className, classIndex, frameW, frameH))

        return detectionsList

    def _applyNms(self, detections: list[Detection]) -> list[Detection]:
        """
        Applies Non-Maximum Suppression to remove duplicates from overlapping tiles.

        Args:
            detections (list[Detection]): The list of all raw detections from all tiles.

        Returns:
            list[Detection]: Filtered list containing only the best unique detections.
        """
        if not detections:
            return []

        boxes = []
        scores = []

        for det in detections:
            w = det.maxX - det.minX
            h = det.maxY - det.minY
            boxes.append([det.minX, det.minY, w, h])
            scores.append(det.confidence)

        indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidenceThreshold, self.iouThreshold)

        finalDetections = []
        if len(indices) > 0:
            for i in indices.flatten():
                finalDetections.append(detections[i])

        return finalDetections
