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
To start the app, run the following command inside the container:
```
gunicorn -k uvicorn.workers.UvicornWorker main:app --workers 2 --bind 0.0.0.0:8000 --timeout 120 --worker-connections 1000
```
# How to run the Voila notebook server for the NFDI Demonstrator
To run the Voila notebook server, use the following command in another terminal inside the same container image:
```voila nfdi.ipynb --template=material --theme=light --port=8888 --Voila.ip=0.0.0.0```
