#!/bin/bash
# Cache sudo password (prompts once at the start)
sudo -v

SESSION="nfdi-demo"

# Kill any existing session with the same name
tmux kill-session -t $SESSION 2>/dev/null

# Start a new tmux session and run the commands
tmux new-session -s $SESSION -d "
  sudo podman start nfdi-demo
  sudo podman exec nfdi-demo redis-server --daemonize yes
  sudo podman exec nfdi-demo bash -c 'export CUDA_VISIBLE_DEVICES=0,1; gunicorn -k uvicorn.workers.UvicornWorker main:app --workers 4 --bind 0.0.0.0:8000 --timeout 120 --worker-connections 1500 --threads 1 --max-requests 300 --max-requests-jitter 30 --worker-tmp-dir /dev/shm'
  sudo podman exec -it nfdi-demo /bin/bash
"

echo "Started in tmux session '$SESSION'. Attach with: tmux attach -t $SESSION"