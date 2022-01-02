import time
import json
import queue
import logging
import datetime

from echo_socket_thread import EchoSocketThread
from libraries.network_thread import NetworkThread


if __name__ == "__main__":

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    test_port: int = 9201

    test_network_thread = NetworkThread(test_port)
    test_network_thread.start()

    test_client = EchoSocketThread(test_port)
    test_client.start()

    time.sleep(1)

    test_duration = 10
    start_time = datetime.datetime.now()
    current_time = datetime.datetime.now()
    run_duration = (current_time - start_time).total_seconds()
    test_message: dict = {"Test": bytes(50000).decode()}

    if test_client.socket_connected:
        test_network_thread.send_message_to_all(test_message)

    while run_duration < test_duration:
        current_time = datetime.datetime.now()
        run_duration = (current_time - start_time).total_seconds()
        try:
            message = test_network_thread.get_incoming_message(.01)
            test_network_thread.send_message_to_all(message)

        except queue.Empty:
            pass

    test_network_thread.stop()
    test_client.stop()

    test_message_str: str = json.dumps(test_message)
    message_size: int = len(test_message_str)
    messages_per_second: int = test_client.messages_echoed // test_duration
    bytes_per_second: int = int(message_size * messages_per_second)

    print("Messages per second:", messages_per_second)
    print("MB per second:", bytes_per_second / (1 << 20))
