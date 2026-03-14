# Ways to improve FPS

## Choose MAXN power mode

```sudo nvpmodel -m 2```


## Lock clocks to a maximum of a current power mode

```sudo jetson_clocks --store```
(Revert with --restore flag)


## Compile model with batching


## Try SAHI library for slicing


## Compile model to TensorRT


## Compile model with FP16 weights


## Adjust video encoding/decoding (Gstream)


## DeepStream (a lot of changes)


## Test plan
Essential configuration of model for export to TensorRT. More models will be compiled, these are just first to check.
### Global Export Configuration
All models must be compiled to TensorRT engines using the following base parameters to ensure hardware acceleration:
    format='engine'
    half=True
    simplify=True

### Baseline Tiled Inference
yolo11n | imgsz=640 | batch=8 | dynamic=True
    Rationale: Absolute baseline. Evaluates the lightest network with standard tile dimensions to establish maximum achievable throughput (FPS) for tiled inference.
yolo11n | imgsz=960 | batch=8 | dynamic=True
    Rationale: Hardware optimization test. Increases input resolution to reduce the total number of tiles per 4K frame. This theoretically decreases the CPU-bound Non-Maximum Suppression (NMS) overhead.
yolo11s | imgsz=640 | batch=8 | dynamic=True
    Rationale: Accuracy scaling test. Evaluates the latency penalty of utilizing a deeper network (Small vs. Nano) to improve feature extraction and reduce false positives.
yolo11s | imgsz=960 | batch=4 | dynamic=True
    Rationale: Maximum standard precision. The batch size is reduced to 4 to prevent VRAM Out-Of-Memory (OOM) exceptions on the Jetson device while processing high-resolution tiles.

### Full-Frame Downscaling (Fallback)
yolo11n | imgsz=1536 | batch=1 | dynamic=False
    Rationale: High-resolution full-frame inference. Compresses the native 4K input directly to 1536x1536. This is expected to yield maximum FPS at the potential cost of completely losing distant drone features due to pixel interpolation.