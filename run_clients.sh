#!/bin/bash

NUM_CLIENTS=5  # Change this to spawn more or fewer clients

echo "📡 Launching $NUM_CLIENTS simulated clients..."

for ((i = 1; i <= NUM_CLIENTS; i++)); do
    echo "🔌 Starting client $i"
    PYTHONPATH=. python client/client.py $i &
done

echo "🕵️‍♀️ All clients running in background. Press Ctrl+C to stop."
wait
