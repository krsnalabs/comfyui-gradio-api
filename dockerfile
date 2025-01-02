# Use Python base image
FROM python:3.10-slim

# Install wget and git for downloading files
RUN apt-get update && apt-get install -y wget git

# Set working directory
WORKDIR /app

# Install comfy-cli
RUN pip install comfy-cli

# Initialize comfyui non-interactively with NVIDIA support
RUN comfy --skip-prompt install --nvidia

# Download your workflow (using raw GitHub URL)
RUN wget https://raw.githubusercontent.com/krsnalabs/comfyui-gradio-api/master/workflow.json

# Install workflow dependencies
RUN comfy node install-deps --workflow=workflow.json

# Install gdown and download models
WORKDIR /root/comfy/ComfyUI
RUN pip install gdown && \
    mkdir -p models/CatVTON && \
    gdown https://drive.google.com/drive/folders/1TJNNql7UfDPVgHJuItDDjowycN5jpC5o -O models/CatVTON --folder

# Reset working directory to /app
WORKDIR /app

# Expose the port that ComfyUI will run on
EXPOSE 8000

# For RunPod, listen on 0.0.0.0 to allow external connections
CMD ["comfy", "launch", "--background", "--", "--listen", "0.0.0.0", "--port", "8000"]