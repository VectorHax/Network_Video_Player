# echo_socket_process.py
# Created by: Dale Best
# Created on: January 2nd, 2022

# A helper class that acts as an echo socket process

# The native python libraries
import queue
import ctypes
import socket
import logging
import datetime
import multiprocessing

# The local libraries
from libraries.socket_thread import SocketThread


class EchoSocketProcess(multiprocessing.Process):
    _DEFAULT_TIMEOUT: float = 1.0

    def __init__(self, port: int):
        assert isinstance(port, int) and port > 0

        multiprocessing.Process.__init__(self)

        self._echo_port: int = port

        self._echo_socket: socket.socket
        self._echo_socket = None

        self._socket_connected = multiprocessing.Value(ctypes.c_bool)
        self._connect_time = multiprocessing.Value(ctypes.c_double)

        self._incoming_queue: queue.Queue
        self._incoming_queue = None

        self._outgoing_queue: queue.Queue
        self._outgoing_queue = None

        self._socket_thread: SocketThread
        self._socket_thread = None

        self._messages_echoed = multiprocessing.Value(ctypes.c_uint)
        self._process_running = multiprocessing.Value(ctypes.c_bool)
        return

    @property
    def messages_echoed(self) -> int:
        return self._messages_echoed.value

    @property
    def socket_connected(self) -> bool:
        return self._socket_connected.value

    def run(self):

        self._process_running.value = True
        self._incoming_queue: queue.Queue = queue.Queue()
        self._outgoing_queue: queue.Queue = queue.Queue()

        while self._process_running.value:
            try:
                if not self._socket_connected.value:
                    self._connect_to_echo_server()

                else:
                    self._echo_message()

            except Exception as echo_error:
                logging.error("Got error with echo socket: " + str(echo_error))

        self._close_echo_socket()
        return

    def stop(self) -> None:
        self._process_running.value = False
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

            current_timestamp = datetime.datetime.utcnow().timestamp()
            self._connect_time.value = current_timestamp
            self._socket_connected.value = True
            self._messages_echoed.value = 0

            logging.debug("Echo Socket Thread connected to the echo server")

        except socket.error:
            self._close_echo_socket()

        return

    def _close_echo_socket(self) -> None:
        self._client_connected = False

        if isinstance(self._echo_socket, socket.socket):
            try:
                self._echo_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

            try:
                self._echo_socket.close()

            except OSError:
                pass

        return

    def _echo_message(self) -> None:
        try:
            message: dict = self._incoming_queue.get(True, .1)
            self._outgoing_queue.put(message)
            self._messages_echoed.value += 1

        except queue.Empty:
            pass

        return
