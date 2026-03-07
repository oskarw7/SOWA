import os
import shutil
import torch
import datetime
from ultralytics import YOLO

modelsToProcess = [
    'yolo11n.pt',
    'yolo11s.pt'
]

exportConfig = {
    'format': 'engine',
    'device': 0,
    'half': True,
    'imgsz': 640
}

exportConfigBatch = {
    'format': 'engine',
    'device': 0,
    'half': True,
    'dynamic': True,
    'imgsz': 640,
    'batch': 8,
    'simplify': True # Needs to be checked
}

def runConversion():
    exportDir = "converted_models"
    os.makedirs(exportDir, exist_ok=True)
    
    currentTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    for modelName in modelsToProcess:
        print(f"\n{'='*50}")
        print(f"[*] Processing: {modelName}")
        print(f"{'='*50}")

        try:
            model = YOLO(modelName)
            enginePath = model.export(**exportConfigBatch)
            
            if enginePath and os.path.exists(enginePath):
                baseName = os.path.basename(enginePath)
                namePart, extPart = os.path.splitext(baseName)
                
                newFileName = f"{namePart}_{currentTime}{extPart}"
                newPath = os.path.join(exportDir, newFileName)
                
                shutil.move(enginePath, newPath)
                print(f"[+] Success: {newPath}")
            
            del model
            torch.cuda.empty_cache()

        except Exception as e:
            print(f"[!] Error for {modelName}: {e}")

if __name__ == "__main__":
    runConversion()