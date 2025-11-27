#!/bin/bash

SESSION="nfdi-demo"

# If the session does not exist, start it
if ! tmux has-session -t $SESSION 2>/dev/null; then
  ./start_site.sh
  # Wait a moment to ensure the session starts
  sleep 1
fi

# Attach to the session
tmux attach -t $SESSION