#!/bin/bash

echo "Stoping client.py process"
# Fetch the PID of the process using pgrep
echo "Finding client.py process-id"
pid=$(pgrep -f "Python client.py")

# Kill the process if the PID is found
if [[ -n $pid ]]; then
    kill $pid
    echo "Process with PID $pid has been terminated."
else
    echo "Process not found or already terminated."
fi

echo "Stoping server.py process"
# Fetch the PID of the process using pgrep
echo "Finding server.py process-id"
pid=$(pgrep -f "Python server.py")

# Kill the process if the PID is found
if [[ -n $pid ]]; then
    kill $pid
    echo "Process with PID $pid has been terminated."
else
    echo "Process not found or already terminated."
fi