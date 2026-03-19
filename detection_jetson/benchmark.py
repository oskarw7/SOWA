import os
import time
import torch
import cv2
import numpy as np
import csv
from datetime import datetime
from detector import Detector

def runVideoBenchmark():
    modelsDir = "converted_models"
    videoSource = "inference_input/drone1_mov5.mov"
    resultsDir = "benchmark_results"
    maxFrames = 100
        
    modelFiles = [f for f in os.listdir(modelsDir) if f.endswith('.engine')]
    
    if not os.path.exists(videoSource):
        print(f"Video source not found: {videoSource}")
        return

    os.makedirs(resultsDir, exist_ok=True)

    print(f"\n\n{'='*50}")
    print(f"VIDEO BENCHMARK - Source: {os.path.basename(videoSource)}")
    print(f"{'='*50}")

    currentTime = datetime.now().strftime("%Y%m%d_%H%M%S")
    csvFilename = os.path.join(resultsDir, f"benchmark_results_{currentTime}.csv")
    
    with open(csvFilename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Model", "Dynamic", "Batch Size", "Image Size", "Function", "Frames", "Avg Latency (ms)", "FPS"])

    for modelFile in modelFiles:
        modelPath = os.path.join(modelsDir, modelFile)
        cap = cv2.VideoCapture(videoSource)
        
        # Parsing, format: modelId_precision_dynamic_batch_imgsz_simplify.extPart
        filenameNoExt = os.path.splitext(modelFile)[0]
        parts = filenameNoExt.split('_')
        
        try:
            precision = parts[-5]
            isDynamic = parts[-4] == 'True'
            batchSize = int(parts[-3])
            modelImgSz = int(parts[-2])
        except (IndexError, ValueError):
            isDynamic = False
            batchSize = 1
            modelImgSz = 640

        detector = Detector(
            modelPath=modelPath, 
            confidenceThreshold=0.5,
            tileSize=modelImgSz,
            batchSize=batchSize,
            precision=precision,
            overlap=0.1
        )
        
        latencies = []
        frameCount = 0
        
        print(f"\n\nTesting: {modelFile}\n")
        
        if not isDynamic and batchSize == 1:
            inferenceFunc = detector.detect
            funcName = "detect"
        elif isDynamic and batchSize > 1:
            inferenceFunc = detector.detectTiledBatch
            funcName = "detectTiledBatch"
        else:
            inferenceFunc = detector.detectTiled
            funcName = "detectTiled"
            
        print(f"Using: {funcName} (batch={batchSize}, imgsz={modelImgSz})")
        
        # Warm-up
        ret, frame = cap.read()
        if ret:
            inferenceFunc(frame) 

        while frameCount < maxFrames:
            ret, frame = cap.read()
            if not ret:
                break
                
            startTime = time.perf_counter()
            inferenceFunc(frame) 
            endTime = time.perf_counter()
            
            latencies.append((endTime - startTime) * 1000)
            frameCount += 1

        cap.release()
        
        if latencies:
            avgLatency = np.mean(latencies)
            avgFps = 1000 / avgLatency
            print(f"Processed {frameCount} frames")
            print(f"Average Latency: {avgLatency:.2f} ms")
            print(f"Real-world Performance: {avgFps:.2f} FPS")

            with open(csvFilename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    modelFile, 
                    isDynamic, 
                    batchSize, 
                    modelImgSz, 
                    funcName, 
                    frameCount, 
                    round(avgLatency, 2), 
                    round(avgFps, 2)
                ])

        del detector
        torch.cuda.empty_cache()

    print(f"\n{'='*50}")
    print(f"BENCHMARK COMPLETE - Results saved to: {csvFilename}")
    print(f"{'='*50}")

if __name__ == "__main__":
    runVideoBenchmark()