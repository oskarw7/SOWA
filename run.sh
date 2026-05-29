#!/bin/bash

# This script works when there is a git worktree folder in root directory of the project.
# It runs detection and mm in parallel

SESSION="dual-run"


if [ ! -p "/tmp/rura" ]; then
    rm -f /tmp/rura
    echo "Robie rure"
    mkfifo /tmp/rura
fi


tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
    tmux kill-session -t $SESSION
fi

if [ $1 == "-t" ]; then
    tmux new-session -d -s $SESSION "cd ../detection_jetson && just test"
else    
    tmux new-session -d -s $SESSION "cd ../detection_jetson && just run"
fi

tmux split-window -h -t $SESSION "cd middle-module && make build && sudo make run"

tmux attach-session -t $SESSION
