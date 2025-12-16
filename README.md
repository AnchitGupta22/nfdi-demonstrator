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
# Install the redis server
Inside the container, run the following commands to install the Redis server:
```
apt-get update && apt-get install -y redis-server
```
# Starting the web app

First start the redis server
```bash
redis-server --daemonize yes
```

Then, start the web app.

## Multi-GPU Systems (2 GPUs)

### CURRENT:
```bash
export CUDA_VISIBLE_DEVICES=0,1
gunicorn -k uvicorn.workers.UvicornWorker main:app \
  --workers 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --worker-connections 1500 \
  --threads 1 \
  --max-requests 300 \
  --max-requests-jitter 30 \
  --worker-tmp-dir /dev/shm
```

# How to run the Voila notebook server for the NFDI Demonstrator
To run the Voila notebook server, use the following command in another terminal inside the same container image:
```voila nfdi.ipynb --template=material --theme=light --port=8001 --Voila.ip=0.0.0.0```
