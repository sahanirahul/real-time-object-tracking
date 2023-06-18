import pytest
import os
from source.ball_bouncing import BouncingBallVideoStreamTrack
from multiprocessing import Value,Queue
from source.server import calculate_coordinates_error
from source.client import calculate_coordinates, process_a
from source.helper import create_file
from source.Logger.logger import setup_logging

logger = setup_logging("test", create_file(os.path.join(os.getcwd(), "logs"), "test.log"))

def test_calculate_coordinates_error():
    # Create a dummy BouncingBallVideoStreamTrack object
    width, height = 640, 480
    bouncing_ball = BouncingBallVideoStreamTrack(width, height)
    bouncing_ball.cur_x_coordinate = 100
    bouncing_ball.cur_y_coordinate = 200
    message = '[100, 200]'

    # Call the calculate_coordinates_error function
    error = calculate_coordinates_error(bouncing_ball, message, logger)

    # Assert that the error is correct
    assert error[0] == 0
    assert error[1] == 0

    bouncing_ball.cur_x_coordinate = 150
    bouncing_ball.cur_y_coordinate = 150
    message = '[100, 200]'

    # Call the calculate_coordinates_error function
    error = calculate_coordinates_error(bouncing_ball, message, logger)
    # Assert that the error is correct
    assert error[0] == 50
    assert error[1] == -50


# Test calculate_coordinates function
def test_calculate_coordinates():
    # Test with a sample image and expected coordinates
    width, height = 640, 480
    bouncing_ball = BouncingBallVideoStreamTrack(width, height,10,10,5)

    frame = bouncing_ball.frames[0]
    x, y = bouncing_ball.coordinates[0]
    image = frame.to_ndarray(format="bgr24")
    x_coordinate = Value('i', 0)
    y_coordinate = Value('i', 0)
    new_coordinates_generated = Value('b', False)

    calculate_coordinates(image, x_coordinate, y_coordinate, new_coordinates_generated, logger)

    assert x_coordinate.value < x + 10 and x_coordinate.value > x - 10  # Expected x-coordinate value
    assert y_coordinate.value < y + 10 and y_coordinate.value > y - 10  # Expected y-coordinate value
    assert new_coordinates_generated.value == True


    frame = bouncing_ball.frames[7]
    x, y = bouncing_ball.coordinates[7]
    image = frame.to_ndarray(format="bgr24")
    x_coordinate = Value('i', 0)
    y_coordinate = Value('i', 0)
    new_coordinates_generated = Value('b', False)

    calculate_coordinates(image, x_coordinate, y_coordinate, new_coordinates_generated, logger)

    assert x_coordinate.value < x + 10 and x_coordinate.value > x - 10  # Expected x-coordinate value
    assert y_coordinate.value < y + 10 and y_coordinate.value > y - 10  # Expected y-coordinate value
    assert new_coordinates_generated.value == True

# Test process_a function
def test_process_a():
   # Test with a sample image and expected coordinates
    width, height = 640, 480
    bouncing_ball = BouncingBallVideoStreamTrack(width, height,10,10,5)
    image_queue = Queue()
    frame = bouncing_ball.frames[0]
    x, y = bouncing_ball.coordinates[0]
    image = frame.to_ndarray(format="bgr24")
    x_coordinate = Value('i', 0)
    y_coordinate = Value('i', 0)
    new_coordinates_generated = Value('b', False)
    image_queue.put(image)
    
    # Call the process_a function
    process_a(image_queue, x_coordinate, y_coordinate, new_coordinates_generated,logger)
    
    assert x_coordinate.value < x + 10 and x_coordinate.value > x - 10  # Expected x-coordinate value
    assert y_coordinate.value < y + 10 and y_coordinate.value > y - 10  # Expected y-coordinate value
    assert new_coordinates_generated.value == True

    frame = bouncing_ball.frames[9]
    x, y = bouncing_ball.coordinates[9]
    image = frame.to_ndarray(format="bgr24")
    x_coordinate = Value('i', 0)
    y_coordinate = Value('i', 0)
    new_coordinates_generated = Value('b', False)
    image_queue.put(image)
    
    # Call the process_a function
    process_a(image_queue, x_coordinate, y_coordinate, new_coordinates_generated)
    
    assert x_coordinate.value < x + 10 and x_coordinate.value > x - 10  # Expected x-coordinate value
    assert y_coordinate.value < y + 10 and y_coordinate.value > y - 10  # Expected y-coordinate value
    assert new_coordinates_generated.value == True


# Run the tests
if __name__ == "__main__":
    pytest.main(['-v'])
