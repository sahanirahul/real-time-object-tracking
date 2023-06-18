import asyncio,time
import cv2
import numpy as np
from aiortc import VideoStreamTrack
from av import VideoFrame

class BouncingBallVideoStreamTrack(VideoStreamTrack):
    """
    A video track that returns a continuous 2D image of a bouncing ball with radius=10 and speed=5.
    """
    def __init__(self, width: int = 640, height: int = 480, num_of_frames: int = 300, radius: int = 10, speed: int = 5):
        """
        Initialize a new BouncingBall object with initial position (width/2.height/2)

        Args:
            width (int, optional): The width of the frame. Defaults to 640.
            height (int, optional): The height of the frame. Defaults to 480.
            num_of_frames (int, optional): Number of frames to generate. Defaults to 300.
            radius (int, optional): Radius of the ball. Defaults to 10.
            speed (int, optional): The speed of the ball. Defaults to 5.
        """
        super().__init__()
        self.counter = 0
        self.cur_x_coordinate = 0
        self.cur_y_coordinate = 0
        # self.logger = None
        # Ball parameters
        ball_radius = radius
        ball_color = (0, 0, 255)  # Blue color (rgb)
        ball_speed = speed
        # Create an empty canvas
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)

        # Initial ball position and speed
        ball_x = int(width/2)
        ball_y = int(height/2)

        ball_velocity_x = ball_speed
        ball_velocity_y = ball_speed

        # list to store the generated frames and coordinates
        self.frames = []
        self.coordinates = []

        for _ in range(num_of_frames):
            self.canvas.fill(0)
            # Update ball position based on velocity
            ball_x += ball_velocity_x
            ball_y += ball_velocity_y

            # Check for collisions with screen boundaries
            if ball_x < ball_radius or ball_x >= width - ball_radius:
                ball_velocity_x *= -1
            if ball_y < ball_radius or ball_y >= height - ball_radius:
                ball_velocity_y *= -1

            # Draw the ball on the canvas
            cv2.circle(self.canvas, (ball_x, ball_y), ball_radius, ball_color, -1)
            # Create a VideoFrame from the canvas image
            frame = VideoFrame.from_ndarray(self.canvas, format="bgr24")
            self.frames.append(frame)
            xy_coordinates = (ball_x,ball_y)
            self.coordinates.append(xy_coordinates)
    async def recv(self):
        """
        Returns next video frame
        """
        pts, time_base = await self.next_timestamp()
        frame = self.frames[self.counter % len(self.frames)]
        xy = self.coordinates[self.counter % len(self.coordinates)]
        frame.pts = pts
        frame.time_base = time_base
        self.cur_x_coordinate = xy[0]
        self.cur_y_coordinate = xy[1]
        self.counter += 1
        return frame

if __name__ == "__main__":
    video_track = BouncingBallVideoStreamTrack()

    # Testing the video track
    loop = asyncio.get_event_loop()
    try:
        async def consume_frames():
            while True:
                frame = await video_track.recv()
                image = frame.to_ndarray()
                cv2.imshow("Bouncing Ball", image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        loop.run_until_complete(consume_frames())
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        loop.run_until_complete(video_track.stop())
