import os
import asyncio
import cv2
import json
from multiprocessing import Value, Queue, Process
from aiortc.contrib.signaling import BYE, TcpSocketSignaling
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
from Logger.logger import setup_logging
from helper import create_file

image_queue = Queue()
x_coordinate = Value('i', 0)
y_coordinate = Value('i', 0)
new_coordinates_generated = Value('b', False)

def calculate_coordinates(image, x_coordinate, y_coordinate, new_coordinates_generated, logger):
    """
    Calculate the coordinates of the ball based on the given image.

    Args:
        image: The image containing the ball.
        x_coordinate: The shared Value for storing the x-coordinate of the ball.
        y_coordinate: The shared Value for storing the y-coordinate of the ball.
        new_coordinates_generated: The shared Value indicating if new coordinates are generated.
        logger: The logger object for logging messages.
    """
    # logger.info("inside calculate_coordinates")
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to separate the ball from the background
    _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)

    # Find contours in the thresholded image, detect objects (ball)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the contour with the largest area, this will give the ball
    contour = max(contours, key=cv2.contourArea)

    # Find the minimum enclosing circle of the contour
    ((center_x, center_y), radius) = cv2.minEnclosingCircle(contour)
    x_coordinate.value = int(center_x)
    y_coordinate.value = int(center_y)
    new_coordinates_generated.value = True
    data = (x_coordinate.value, y_coordinate.value, new_coordinates_generated.value)
    logger.info(f"calculated_coordinates = {data}")

async def create_data_channel(pc, signaling,logger):
    """
    Create a data channel for sending coordinates to the remote party.

    Args:
        pc: The RTCPeerConnection object.
        signaling: The signaling object used for signaling.
    """
    channel = pc.createDataChannel("coordinates")
    logger.info("channel({}) - created by local party".format(channel.label))

    async def send_coordinates():
        while True:
            if new_coordinates_generated.value:
                new_coordinates_generated.value = False
                data = (x_coordinate.value, y_coordinate.value)
                data_str = json.dumps(data)
                logger.info("channel(%s) --> %s" % (channel.label, data_str))
                channel.send(data_str)
            await asyncio.sleep(.001)  # sending data every 1 ms,this is to reduce load to the cpu

    @channel.on("open")
    def on_open():
        asyncio.ensure_future(send_coordinates())
    logger.info("sending offer signal")
    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(pc.localDescription)


def process_a(image_queue: Queue, x_coordinate: Value, y_coordinate: Value, new_coordinates_generated: Value, logger: any=None):
    """
    Process for calculating coordinates from the image frames.

    Args:
        image_queue: The Queue for receiving image frames.
        x_coordinate: The shared Value for storing the x-coordinate of the ball.
        y_coordinate: The shared Value for storing the y-coordinate of the ball.
        new_coordinates_generated: The shared Value indicating if new coordinates are generated.
        logger: The logger object for logging messages.
    """
    if logger == None:
        logger = setup_logging("client_process_a", create_file(os.path.join(os.getcwd(), "logs"),"client_process_a.log"))
        logger.info("process_a started")
    while True:
        # logger.info("fetching image from queue")
        image = image_queue.get()
        if image is None:
            break
        # logger.info("image coordinates calculation started")
        calculate_coordinates(image, x_coordinate, y_coordinate, new_coordinates_generated, logger)
        # logger.info("image coordinates calculation finished")


async def run(pc: RTCPeerConnection, signaling: TcpSocketSignaling,logger):
    """
    Main function for running the client.

    Args:
        pc: The RTCPeerConnection object.
        signaling: The signaling object used for signaling.
    """
    await signaling.connect()

    @pc.on("track")
    def on_track(track):
        logger.info("Receiving = {}".format(track.kind))
        asyncio.ensure_future(process_track(track))

    async def process_track(track):
        while True:
            frame = await track.recv()
            image = frame.to_ndarray(format="bgr24")
            image_queue.put(image)
            cv2.imshow("Received Frames", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            await asyncio.sleep(0.01)

    data_channel_created = False
    while True:
        try:
            logger.info("waiting to receive signal")
            obj = await signaling.receive()
            if isinstance(obj, RTCSessionDescription):
                logger.info("RTCSessionDescription: signaling_state={} object_type={}".format(pc.signalingState, obj.type))
                if pc.signalingState == "have-local-offer":
                    if obj.type == "answer":
                        await pc.setRemoteDescription(obj)
                else:
                    if obj.type == "offer":
                        # send answer
                        await pc.setRemoteDescription(obj)
                        await pc.setLocalDescription(await pc.createAnswer())
                        logger.info("sending to answer signal")
                        await signaling.send(pc.localDescription)
                        if not data_channel_created:
                            await create_data_channel(pc, signaling,logger)
                            data_channel_created = True
            elif isinstance(obj, RTCIceCandidate):
                logger.info("RTCIceCandidate_received")
                await pc.addIceCandidate(obj)
            elif obj is BYE:
                logger.info("received_bye_signal_exiting")
                break
        except Exception as e:
            logger.error("error_while_consuming_signal={}".format(e))
            continue


if __name__ == "__main__":
    log_file_path = create_file(os.path.join(os.getcwd(), "logs"),"client.log")
    print(f"Logging in file: {log_file_path}")
    logger = setup_logging("client", log_file_path)
    logger.info("started_client")
    image_process = Process(target=process_a, args=(image_queue, x_coordinate, y_coordinate, new_coordinates_generated))
    image_process.start()
    logger.info("started_process_a")
    signaling = TcpSocketSignaling("localhost", 9000)
    logger.info("prepared tcp-socket-signaling object")
    pc = RTCPeerConnection()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            run(
                pc=pc,
                signaling=signaling,
                logger=logger,
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(signaling.close())
        loop.run_until_complete(pc.close())
        image_process.join()
