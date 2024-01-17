import socket
from time import time
import message
from utilities import INFO_HASH, generate_client_id
import select
import errno
import logging
from struct import unpack


class Peer:
    def __init__(self, ip, port=6881):
        self.states = {
            'peer_choking': True,
            'peer_interested': False
        }
        self.ip_address = ip
        self.port = port
        self.socket = None
        self.last_call = 0.0
        self.healthy = False
        self.buffer = b""
        self.last_keep_alive_time = time()

    @staticmethod
    def __read_buffer(self):
        # parameter for socket.recv function should be small power of 2 -> 4096 (2^12)
        buffer_size = 4096
        self.socket.setblocking(False)
        while True:
            try:
                ready_to_read, _, _ = select.select([self.socket], [], [], 1)
                if ready_to_read:
                    buffer = self.socket.recv(buffer_size)
                    if len(buffer) <= 0:
                        break
                    self.buffer += buffer
                else:
                    break
            except socket.error as e:
                # buffer is empty
                if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                    pass
                else:
                    print(f"Socket-related error occur: ({e.args[0]}) while reading "
                          f"a buffer for the following socket: {self.socket}")
            except BufferError:
                print(f"BufferError occur while reading a buffer "
                      f"for the following socket: {self.socket}")

        return self.buffer

    @staticmethod
    def __is_handshake(msg):
        return True if msg.startswith(b"\x13BitTorrent protocol") else False

    def handshake(self):
        if self.socket is None:
            return False
        try:
            handshake = message.HandShake(info_hash=INFO_HASH, peer_id=generate_client_id()).to_bytes()
            self.send_message(msg=handshake)
            logging.log(logging.INFO, "HandShake was sent to user with following ip: {self.ip_address}")
            return True
        except ConnectionError:
            logging.exception(f"HandShake was not sent to user with following ip: {self.ip_address}")
        return False

    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip_address, self.port), timeout=2)
            self.socket.setblocking(False)
            self.healthy = True
            logging.log(logging.INFO, f"Connection with peer {self.ip_address} established")

        except TimeoutError:
            logging.log(logging.INFO, f"Failed to connect to peer {self.ip_address}")
            return False
        except ConnectionRefusedError:
            logging.log(logging.INFO, f"Connection to peer {self.ip_address} refused")
            return False
        except OSError as e:
            if "[Errno 113] No route to host" in str(e):
                logging.log(logging.INFO, f"No route to host for peer {self.ip_address}")
            else:
                logging.log(logging.INFO, f"OSError: {e}")
            return False

        return True

    def disconnect(self):
        try:
            if self.socket:
                self.socket.close()
            self.healthy = False
        except (socket.error, OSError, AttributeError, BlockingIOError) as e:
            logging.log(logging.INFO, f"Error disconnecting from {self.ip_address}:{self.port}: {e}")

    def send_message(self, msg):
        try:
            self.socket.send(msg)
            self.healthy = True
            self.last_call = time()
        except ConnectionError as ce:
            print(f"Connection error: {ce}")
        except TimeoutError as te:
            print(f"Timeout error: {te}")
        except OSError as oe:
            print(f"OS error: {oe}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def process_handshake_response(self):
        response_message = self.__read_buffer(self)
        logging.info(response_message)
        return self.__is_handshake(response_message)

    def set_keep_alive_call(self):
        self.last_keep_alive_time = time()

    def get_last_keep_alive_call(self):
        return time() - self.last_keep_alive_time

    def send_keep_alive(self):
        if self.socket is None:
            return False
        keep_alive_msg = message.KeepAlive().to_bytes()
        self.send_message(msg=keep_alive_msg)
        self.set_keep_alive_call()

    def send_interested(self):
        interested_msg = message.Interested().to_bytes()
        self.send_message(interested_msg)

    def send_choke(self):
        choke_msg = message.Choke().to_bytes()
        self.send_message(choke_msg)

    def send_unchoke(self):
        unchoke_msg = message.Unchoke().to_bytes()
        self.send_message(unchoke_msg)

    def get_message(self):
        """Determine message type and return it"""
        while self.buffer > 4:
            payload_length, = unpack(">I", self.buffer[:4])
            total_length = payload_length + 4
            if self.buffer < total_length:
                break
            else:
                payload = self.buffer[:total_length]
                self.buffer = self.buffer[total_length:]
            try:
                msg = message.MessageDispatcher(payload_param=payload).dispatch()
                if msg:
                    yield msg
            except message.WrongMessageException as e:
                logging.error(e.__str__())

    def handle_choke(self, msg: message.Choke):
        """Handles message with type Choke"""
        pass

    def handle_unchoke(self, msg: message.Unchoke):
        pass

    def handle_interested(self, msg: message.Interested):
        pass

    def handle_not_interested(self, msg: message.NotInterested):
        pass

    def handle_have(self, msg: message.Have):
        pass