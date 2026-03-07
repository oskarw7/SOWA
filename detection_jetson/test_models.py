import os
import time
import torch
import cv2
import numpy as np
from detector import Detector

def runVideoBenchmark():
    modelsDir = "converted_models"
    videoSource = "inference_input/drone1_mov5.mov"
    maxFrames = 100
    tileSize = 640
    
    modelFiles = [f for f in os.listdir(modelsDir) if f.endswith('.engine')]
    
    if not os.path.exists(videoSource):
        print(f"Video source not found: {videoSource}")
        return

    print(f"\n{'='*50}")
    print(f"VIDEO BENCHMARK - Source: {os.path.basename(videoSource)}")
    print(f"{'='*50}")

    for modelFile in modelFiles:
        modelPath = os.path.join(modelsDir, modelFile)
        cap = cv2.VideoCapture(videoSource)
        detector = Detector(modelPath=modelPath, confidenceThreshold=0.25)
        
        latencies = []
        frameCount = 0
        
        print(f"\nTesting: {modelFile}")
        
        ret, frame = cap.read()
        if ret:
            detector.detectTiled(frame, tileSize=tileSize)

        while frameCount < maxFrames:
            ret, frame = cap.read()
            if not ret:
                break
                
            startTime = time.perf_counter()
            detector.detectTiled(frame, tileSize=tileSize)
            endTime = time.perf_counter()
            
            latencies.append((endTime - startTime) * 1000)
            frameCount += 1

        cap.release()
        
        if latencies:
            avgLatency = np.mean(latencies)
            avgFps = 1000 / avgLatency
            print(f"\nProcessed {frameCount} frames")
            print(f"Average Latency: {avgLatency:.2f} ms")
            print(f"Real-world Performance: {avgFps:.2f} FPS")

        del detector
        torch.cuda.empty_cache()

    print(f"\n{'='*50}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*50}")

if __name__ == "__main__":
    runVideoBenchmark()