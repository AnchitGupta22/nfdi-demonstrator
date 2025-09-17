# Docker steps for NFDI Demonstrator
To create the Docker image for the NFDI Demonstrator, follow these steps:
```
docker build -t nfdi-demonstrator .
docker run -it --runtime=nvidia --gpus all --memory=12g --ipc=host -p 8888:8888 -p 8000:8000
```
To start the container, you can use the following commands:
```
docker start <container-image>
docker exec -it <container-image> bash
```
# Start the redis server
Inside the container, run the following commands to install and start the Redis server:
```
apt-get update && apt-get install -y redis-server
redis-server --daemonize yes
```
# Starting the web app

## Single GPU System - High Concurrency (Recommended for Multiple Users)
```bash
# Optimized for multiple simultaneous user interactions
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers 1 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --worker-connections 4000 \
  --threads 8 \
  --max-requests 500 \
  --max-requests-jitter 50 \
  --worker-tmp-dir /dev/shm \
  --worker-class uvicorn.workers.UvicornWorker
```

## Alternative: Multiple Workers with GPU Sharing (Experimental)
```bash
# Use multiple workers that share the same GPU
# Note: This may cause CUDA memory issues with large models
export CUDA_VISIBLE_DEVICES=0
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers 2 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --worker-connections 2000 \
  --threads 4 \
  --max-requests 250 \
  --max-requests-jitter 25 \
  --worker-tmp-dir /dev/shm
```

## High-Throughput Testing Configuration
```bash
# Maximum concurrency for load testing
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers 1 \
  --bind 0.0.0.0:8000 \
  --timeout 180 \
  --worker-connections 8000 \
  --threads 16 \
  --max-requests 200 \
  --max-requests-jitter 20 \
  --worker-tmp-dir /dev/shm \
  --keep-alive 5 \
  --backlog 2048
```

## Development/Testing with Hot Reload
```bash
# For development with auto-reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --workers 1
```

## Configuration Comparison

| Configuration | Workers | Threads | Connections | Best For |
|---------------|---------|---------|-------------|----------|
| Standard | 1 | 2 | 1000 | Light usage |
| High Concurrency | 1 | 8 | 4000 | **Multiple users** |
| GPU Sharing | 2 | 4 | 2000 | Experimental |
| Load Testing | 1 | 16 | 8000 | Stress testing |

**Key Changes for Multiple Users:**
- `--threads 8` or `--threads 16`: Allows 8-16 simultaneous requests to be processed
- `--worker-connections 4000-8000`: Handles many concurrent connections  
- `--keep-alive 5`: Keeps connections alive for faster subsequent requests
- `--backlog 2048`: Queues more incoming connections
- Reduced `--max-requests`: Workers restart more frequently to prevent memory leaks

Notes:
- `--worker-tmp-dir /dev/shm` uses RAM for temporary files (faster I/O)
- Models are preloaded during startup to eliminate first-request delay
- Higher thread counts work well with async I/O operations
- Monitor GPU memory usage with `nvidia-smi -l 1` during testing
- For serious load testing, consider using multiple containers with a load balancer

## Multi-GPU Systems (2+ GPUs)

### Option 1: Two Workers (One per GPU) - Recommended for 2x A100
```bash
# Each worker gets its own GPU for maximum isolation
export CUDA_VISIBLE_DEVICES=0,1
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers 2 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --worker-connections 2000 \
  --threads 4 \
  --max-requests 500 \
  --max-requests-jitter 50 \
  --worker-tmp-dir /dev/shm \
  --preload
```

### Option 2: Four Workers (2 per GPU) - Maximum Concurrency
```bash
# Higher concurrency with GPU sharing
export CUDA_VISIBLE_DEVICES=0,1
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --worker-connections 1500 \
  --threads 3 \
  --max-requests 300 \
  --max-requests-jitter 30 \
  --worker-tmp-dir /dev/shm
```

### Option 3: Auto-detect GPU Count
```bash
# Automatically use one worker per GPU
export CUDA_VISIBLE_DEVICES=$(nvidia-smi --list-gpus | grep -oP 'GPU \K\d+' | paste -sd,)
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers $(nvidia-smi --list-gpus | wc -l) \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --worker-connections 2000 \
  --threads 4 \
  --max-requests 500 \
  --max-requests-jitter 50 \
  --worker-tmp-dir /dev/shm
```

## Configuration Comparison for Multi-GPU

| Configuration | Workers | GPUs Used | Memory per GPU | Concurrent Users |
|---------------|---------|-----------|----------------|------------------|
| 1 Worker per GPU | 2 | Both | ~16GB each | 8-16 |
| 2 Workers per GPU | 4 | Both | ~16GB each | 16-32 |
| Single GPU (fallback) | 1 | GPU 0 only | ~16GB | 8-16 |

**Multi-GPU Notes:**
- Each A100 32GB can easily handle your thermal simulation models
- `--preload` is safe with multiple workers when models auto-select GPUs
- Monitor with `nvidia-smi -l 1` to verify GPU load balancing
- Consider container orchestration (Docker Swarm/K8s) for production scaling

# How to run the Voila notebook server for the NFDI Demonstrator
To run the Voila notebook server, use the following command in another terminal inside the same container image:
```voila nfdi.ipynb --template=material --theme=light --port=8888 --Voila.ip=0.0.0.0```
