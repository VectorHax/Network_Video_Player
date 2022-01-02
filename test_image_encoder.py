import time
import logging

from libraries.image_encoder_thread import ImageEncoderThread

import numpy

VIDEO_SHAPE: tuple = (1080, 1920, 3)
VIDEO_SIZE: int = VIDEO_SHAPE[0] * VIDEO_SHAPE[1] * VIDEO_SHAPE[2]


def create_random_frame() -> numpy.ndarray:
    random_buffer = numpy.random.randint(0, 255, VIDEO_SIZE)
    random_frame = random_buffer.reshape(VIDEO_SHAPE)
    return random_frame


if __name__ == "__main__":

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    test_frame = create_random_frame()

    test_length: int = 91

    image_encoders = []

    for _ in range(4):
        test_image_encoder = ImageEncoderThread()
        test_image_encoder.start()
        image_encoders.append(test_image_encoder)

    for _ in range(test_length):
        for image_encoder in image_encoders:
            image_encoder.add_image(test_frame)
    
    print("All images added")
    while image_encoders[0].images_encoded < test_length:
        time.sleep(0)

    print("All images encoded")

    for image_encoder in image_encoders:
        image_encoder.stop()

    print("All image encoders stopped")

    encode_times: list = image_encoders[0].encode_timings[:test_length - 1]

    encode_duration: float = sum(encode_times)
    encode_average: float = encode_duration / len(encode_times)
    print("Encode average:", encode_average, "Encoded max:", max(encode_times))
    if encode_average != 0:
        print("Encode FPS:", 1 / encode_average)

    print(encode_times)
