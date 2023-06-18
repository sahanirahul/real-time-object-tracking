#!/bin/bash
echo "starting the server in the background"
python3 server.py >/dev/null 2>&1 &
# python3 server.py >server_start.log 2>&1 &

echo "waiting for 5 sec before starting client"
sleep 5

echo "starting the client in the background"
python3 client.py >/dev/null 2>&1 &
# python3 client.py >clinet_start.log 2>&1 &
