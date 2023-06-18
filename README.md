## Python Application README

This repository contains a Python application that utilizes python's WebRTC library 'aiortc' and 'open-cv' for P2P communication between a server and a client. The server generates video frames of a bouncing ball on a screen and sends them to the client, which receives the images and displays on the screen, creates a data channel with the server, calculates the coordinates of the ball in real-time and sends back to server through the data-channel. The server then calculates the error in current position of the ball and the received position from the client and logs the error.

## Prerequisites

- Python 3.7 or higher
- `aiortc,cv2,multiprocessing,numpy,pytest`

## Usage

### Running the Server

1. Open a terminal and navigate to the project directory.

2. Run the server script:
    python3 server.py

### Running the Client

1. Open another terminal and navigate to the project directory.

2. Run the client script:
    python3 client.py

### Starting and Stopping the programs in the background using script
#### To Start:
```
    sh start.sh
```
#### To Stop:
```
    sh stop.sh
```
### Running tests

1. Add the source folder in the PYTHONPATH environment variable
```
    export PYTHONPATH=/path/to/the/source_directory:$PYTHONPATH
```
2. Run:
```
    pytest test_your_script.py
```