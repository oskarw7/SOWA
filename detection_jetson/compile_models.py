import os
import shutil
import torch
from ultralytics import YOLO

compilationPlan = [
    {'model': 'yolo11n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': True, 'batch': 8, 'imgsz': 640, 'simplify': True},
    {'model': 'yolo11n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': True, 'batch': 8, 'imgsz': 960, 'simplify': True},

    {'model': 'yolo11s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': True, 'batch': 8, 'imgsz': 640, 'simplify': True},
    {'model': 'yolo11s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': True, 'batch': 4, 'imgsz': 960, 'simplify': True},

    {'model': 'yolo26n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': True, 'batch': 8, 'imgsz': 640, 'simplify': True},
    {'model': 'yolo26n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': True, 'batch': 8, 'imgsz': 960, 'simplify': True},

    {'model': 'yolo26s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': True, 'batch': 8, 'imgsz': 640, 'simplify': True},
    {'model': 'yolo26s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': True, 'batch': 4, 'imgsz': 960, 'simplify': True},

    {'model': 'yolo11n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 1536, 'simplify': True},
    {'model': 'yolo11n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 960, 'simplify': True},
    {'model': 'yolo11n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 640, 'simplify': True},

    {'model': 'yolo11s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 1536, 'simplify': True},
    {'model': 'yolo11s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 960, 'simplify': True},
    {'model': 'yolo11s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 640, 'simplify': True},

    {'model': 'yolo26n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 1536, 'simplify': True},
    {'model': 'yolo26n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 960, 'simplify': True},
    {'model': 'yolo26n.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 640, 'simplify': True},

    {'model': 'yolo26s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 1536, 'simplify': True},
    {'model': 'yolo26s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 960, 'simplify': True},
    {'model': 'yolo26s.pt', 'format': 'engine', 'device': 0, 'half': True, 'int8': False, 'dynamic': False, 'batch': 1, 'imgsz': 640, 'simplify': True}
]

# save format:
# modelId_precision_dynamic_batch_imgsz_simplify.extPart
def runConversion():
    exportDir = "converted_models"
    os.makedirs(exportDir, exist_ok=True)

    for config in compilationPlan:
        modelName = config.pop('model')
          
        if config['half']: precision = 'fp16'
        elif config['int8']: precision = 'int8'
        else: precision = 'fp32'

        print(f"\n{'='*50}")
        print(f"Processing: {modelName} | imgsz={config['imgsz']} | batch={config['batch']}")
        print(f"{'='*50}")

        try:
            model = YOLO(modelName)
            enginePath = model.export(**config)

            if enginePath and os.path.exists(enginePath):
                baseName = os.path.basename(enginePath)
                namePart, extPart = os.path.splitext(baseName)
                
                newFileName = f"{namePart}_{precision}_{config['dynamic']}_{config['batch']}_{config['imgsz']}_{config['simplify']}{extPart}"
                newPath = os.path.join(exportDir, newFileName)

                shutil.move(enginePath, newPath)
                print(f"Success: {newPath}")

            del model
            torch.cuda.empty_cache()

        except Exception as e:
            print(f"Error for {modelName}: {e}")

if __name__ == "__main__":
    runConversion()