#!/bin/bash
set -e

sudo apt-get update
sudo apt-get install -y python3-pip libopenblas-dev libcusparselt0 libcusparselt-dev \
                        python3-libnvinfer-dev tensorrt nvidia-cuda nvidia-cudnn \
                        libglib2.0-0 libsm6 libxext6 libxrender-dev

rm -rf .venv uv.lock

if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

uv cache clean
uv venv --python 3.10 --system-site-packages
source .venv/bin/activate

uv pip install --upgrade --force-reinstall --no-cache-dir \
    torch torchvision \
    --index-url https://pypi.jetson-ai-lab.io/jp6/cu126

uv pip install --upgrade --no-cache-dir \
    "numpy<2.0" \
    ultralytics \
    onnx \
    onnxslim \
    matplotlib

uv pip install https://github.com/ultralytics/assets/releases/download/v0.0.0/onnxruntime_gpu-1.23.0-cp310-cp310-linux_aarch64.whl

rm -rf .venv/lib/python3.10/site-packages/tensorrt
ln -sf /usr/lib/python3.10/dist-packages/tensorrt .venv/lib/python3.10/site-packages/

export LD_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu/nvidia:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
python3 -c "import torch; import tensorrt; import numpy; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'TensorRT: {tensorrt.__version__}'); print(f'NumPy: {numpy.__version__}')"