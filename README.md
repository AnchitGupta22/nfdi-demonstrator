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
To start the app (recommended for GPU-backed workers), run inside the container:

```bash
# Optimized settings for faster startup and response
# for a single GPU system:
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers 1 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --worker-connections 1000 \
  --threads 2 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --worker-tmp-dir /dev/shm
```

For even faster startup, you can preload the application (CPU models only):
```bash
# Only use --preload if models are CPU-only or you handle CUDA contexts properly
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers 1 \
  --bind 0.0.0.0:8000 \
  --preload \
  --timeout 120 \
  --worker-connections 1000 \
  --threads 2 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --worker-tmp-dir /dev/shm
```

Notes:
- `--worker-tmp-dir /dev/shm` uses RAM for temporary files (faster I/O)
- Models are now preloaded during startup to eliminate first-request delay
- Do NOT use --preload when loading GPU models (it creates CUDA context in master process). If your models are CPU-only, --preload is fine.
- For multi-GPU machines, run one gunicorn process (or container) per GPU, or use a process manager to pin workers to specific CUDA_VISIBLE_DEVICES.

# How to run the Voila notebook server for the NFDI Demonstrator
To run the Voila notebook server, use the following command in another terminal inside the same container image:
```voila nfdi.ipynb --template=material --theme=light --port=8888 --Voila.ip=0.0.0.0```
