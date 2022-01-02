# echo_socket_thread.py
# Created by: Dale Best
# Created on: January 2nd, 2022

# A helper class that acts as an echo socket thread


# The native python libraries
import datetime
import queue
import socket
import logging
import threading

# The local libraries
from libraries.socket_thread import SocketThread


class EchoSocketThread(threading.Thread):

    _DEFAULT_TIMEOUT: float = 1.0

    def __init__(self, port: int):
        assert isinstance(port, int) and port > 0

        threading.Thread.__init__(self)

        self._echo_port: int = port

        self._echo_socket = socket.socket()

        self._socket_connected: bool = False
        self._connect_time = datetime.datetime.utcnow()

        self._incoming_queue = queue.Queue()
        self._outgoing_queue = queue.Queue()

        self._socket_thread: SocketThread
        self._socket_thread = None

        self._messages_echoed: int = 0
        self._thread_running = False
        return

    @property
    def messages_echoed(self) -> int:
        return self._messages_echoed

    @property
    def socket_connected(self) -> bool:
        return self._socket_connected

    def run(self):

        self._thread_running = True

        while self._thread_running:
            try:
                if not self._socket_connected:
                    self._connect_to_echo_server()

                else:
                    self._echo_message()

            except Exception as echo_error:
                logging.error("Got error with echo socket: " + str(echo_error))

        self._close_echo_socket()
        return

    def stop(self) -> None:
        self._thread_running = False
        self.join()
        return

    def _connect_to_echo_server(self) -> None:
        try:
            self._echo_socket = socket.socket()
            self._echo_socket.settimeout(self._DEFAULT_TIMEOUT)
            self._echo_socket.connect(("127.0.0.1", self._echo_port))
            self._socket_thread = SocketThread(self._echo_socket,
                                               self._incoming_queue,
                                               self._outgoing_queue)
            self._socket_thread.start()

            self._connect_time = datetime.datetime.utcnow()
            self._socket_connected = True
            self._messages_echoed = 0

            logging.debug("Echo Socket Thread connected to the echo server")

        except socket.error:
            self._close_echo_socket()

        return

    def _echo_message(self) -> None:
        try:
            message: dict = self._incoming_queue.get(True, .1)
            self._outgoing_queue.put(message)
            self._messages_echoed += 1

        except queue.Empty:
            pass

        return

    def _close_echo_socket(self) -> None:
        self._client_connected = False

        try:
            self._echo_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        try:
            self._echo_socket.close()

        except OSError:
            pass

        return
