from ultralytics import YOLO
import numpy as np
import cv2


class Detection:
    def __init__(self, xMin: int, yMin: int, xMax: int, yMax: int, confidence: float, className: str, classIndex: int, frameW: int, frameH: int):
        self.xMin = xMin
        self.yMin = yMin
        self.xMax = xMax
        self.yMax = yMax
        self.confidence = confidence
        self.className = className
        self.classIndex = classIndex

        # --- Center and Offset Calculation ---
        self.centerX = int((xMin + xMax) / 2)
        self.centerY = int((yMin + yMax) / 2)

        imageCenterX = int(frameW / 2)
        imageCenterY = int(frameH / 2)

        # Offset: (Negative = Left/Up, Positive = Right/Down from center)
        self.offsetX = self.centerX - imageCenterX
        self.offsetY = self.centerY - imageCenterY


class Detector:
    def __init__(self, modelPath: str, confidenceThreshold: float, device: str = '0'):
        # Added device parameter (default '0' for GPU)
        self.device = device
        self.model = YOLO(modelPath, task='detect')
        self.labels = self.model.names
        self.confidenceThreshold = confidenceThreshold

    def detect(self, frame: np.ndarray) -> list[Detection]:
        # Pass device to the model
        return self._process_results(self.model(frame, device=self.device, verbose=False)[0], frame.shape, offset=(0, 0))

    def detect_tiled(self, frame: np.ndarray, tile_size: int = 640, overlap: float = 0.25) -> list[Detection]:
        """
        Splits image into tiles, detects, maps coordinates back, and removes duplicates.
        """
        imgH, imgW = frame.shape[:2]
        step = int(tile_size * (1 - overlap))

        all_detections = []

        # Generate tiles
        for y in range(0, imgH, step):
            for x in range(0, imgW, step):
                x_start = min(x, imgW - tile_size)
                y_start = min(y, imgH - tile_size)

                x_start = max(0, x_start)
                y_start = max(0, y_start)

                crop = frame[y_start:y_start+tile_size, x_start:x_start+tile_size]

                # Pass device to the model
                results = self.model(crop, device=self.device, verbose=False, imgsz=tile_size)

                tile_detections = self._process_results(results[0], frame.shape, offset=(x_start, y_start))
                all_detections.extend(tile_detections)

                if x_start + tile_size >= imgW:
                    break
            if y_start + tile_size >= imgH:
                break

        return self._apply_nms(all_detections)

    def _process_results(self, result, frame_shape, offset: tuple) -> list[Detection]:
        detections_list = []
        boxes = result.boxes
        off_x, off_y = offset
        frame_h, frame_w = frame_shape[:2]

        for i in range(len(boxes)):
            confidence = boxes[i].conf.item()
            if confidence >= self.confidenceThreshold:
                coords = boxes[i].xyxy.cpu().numpy().squeeze()
                xMin, yMin, xMax, yMax = coords.astype(int)

                xMin += off_x
                yMin += off_y
                xMax += off_x
                yMax += off_y

                classIndex = int(boxes[i].cls.item())
                className = self.labels[classIndex]

                detections_list.append(Detection(xMin, yMin, xMax, yMax, confidence, className, classIndex, frame_w, frame_h))

        return detections_list

    def _apply_nms(self, detections: list[Detection], iou_thresh: float = 0.45) -> list[Detection]:
        if not detections:
            return []

        boxes = []
        scores = []

        for det in detections:
            w = det.xMax - det.xMin
            h = det.yMax - det.yMin
            boxes.append([det.xMin, det.yMin, w, h])
            scores.append(det.confidence)

        indices = cv2.dnn.NMSBoxes(boxes, scores, self.confidenceThreshold, iou_thresh)

        final_detections = []
        if len(indices) > 0:
            for i in indices.flatten():
                final_detections.append(detections[i])

        return final_detections
