import asyncio
import json
import os
from Logger.logger import setup_logging
from ball_bouncing import BouncingBallVideoStreamTrack
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.signaling import BYE, TcpSocketSignaling
from helper import create_file

def calculate_coordinates_error(bouncing_ball: BouncingBallVideoStreamTrack, message: str,logger):
    """
    Calculate the error in coordinates based on the received message.

    Args:
        bouncing_ball (BouncingBallVideoStreamTrack): The BouncingBallVideoStreamTrack object.
        message (str): The message containing coordinates in JSON format.
    """
    logger.info("received_coordinates = %s" % (message))
    coordinates = json.loads(message)
    error_x = bouncing_ball.cur_x_coordinate - coordinates[0]
    error_y = bouncing_ball.cur_y_coordinate - coordinates[1]
    error = (error_x, error_y)
    logger.info("calculated_error_in_coordinates = {}".format(error))
    return error

async def run(pc: RTCPeerConnection, signaling: TcpSocketSignaling,logger):
    """
    Create an offer with a video track of a bouncing ball and listen for signals from other peers.

    When receiving an offer, create an answer to listen for messages on the data channel.

    Args:
        pc (RTCPeerConnection): The RTCPeerConnection used for P2P communication.
        signaling (TcpSocketSignaling): The signaling object used for signaling.
    """
    width, height = 640, 480
    bouncing_ball = None
    try:
        bouncing_ball = BouncingBallVideoStreamTrack(width, height)
        bouncing_ball.logger = logger
    except Exception as e:
        logger.error("error_in_creating_bouncing_ball_frames {}".format(e))
    await signaling.connect()
    def add_tracks():
        pc.addTrack(bouncing_ball)

    add_tracks()
    # send initial offer for media track
    await pc.setLocalDescription(await pc.createOffer())
    logger.info("sending offer signal")
    await signaling.send(pc.localDescription)

    # consume signaling
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
                        # send answer for data channel
                        @pc.on("datachannel")
                        def on_datachannel(channel):
                            logger.info("channel({}) - created by remote party".format(channel.label))

                            @channel.on("message")
                            def on_message(message):
                                calculate_coordinates_error(bouncing_ball, message,logger)
                        await pc.setRemoteDescription(obj)
                        await pc.setLocalDescription(await pc.createAnswer())
                        logger.info("sending answer signal")
                        await signaling.send(pc.localDescription)
            elif isinstance(obj, RTCIceCandidate):
                logger.info("RTCIceCandidate_received")
                await pc.addIceCandidate(obj)
            elif obj is BYE:
                logger.info("received_bye_signal_exiting")
                break
        except Exception as e:
            logger.error("error_while_consuming_signal={}".format(e))
            continue
        await asyncio.sleep(0.1)


if __name__ == "__main__":
    log_file_path = create_file(os.path.join(os.getcwd(), "logs"),"server.log")
    print(f"Logging in file: {log_file_path}")
    logger = setup_logging("client", log_file_path)
    logger.info("starting_server")
    signaling = TcpSocketSignaling("localhost", 9000)
    logger.info("prepared tcp-socket-signaling object")
    pc = RTCPeerConnection()
    # run event loop
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
        # cleanup
        loop.run_until_complete(signaling.close())
        loop.run_until_complete(pc.close())
