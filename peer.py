import message
from utilities import INFO_HASH
from block import State
from torrent import generate_client_id

import socket
from time import time
import bitstring
import select
import errno
import logging
from struct import unpack

# TODO: figure out the usage of last_call, now I don't validate in any way difference between curr time and last call


class Peer:
    # FIX: I don't like the way how I pass number_of_pieces, utilities.py has a function for this
    def __init__(self, piece_manager, number_of_pieces, ip, port=6881):
        self.piece_manager = piece_manager

        self.states = {
            'peer_choking': True,
            'peer_interested': False,
            'am_choking': True,
            'am_interested': False
        }
        self.handshake_provided = False
        self.ip_address = ip
        self.port = port
        self.socket = None
        self.last_call = 0.0
        self.healthy = False
        self.buffer = b""
        self.last_keep_alive_time = time()
        self.bitfield_size = number_of_pieces
        self.bitfield = bitstring.BitArray(self.bitfield_size)

    def has_piece(self, piece_index):
        return self.bitfield[piece_index]

    def read_buffer(self):
        data = b""
        # parameter for socket.recv function should be small power of 2 -> 4096 (2^12)
        buffer_size = 4096
        self.socket.setblocking(False)
        while True:
            try:
                ready_to_read, _, _ = select.select([self.socket], [], [], 1)
                if ready_to_read:
                    self.buffer = self.socket.recv(buffer_size)
                    if len(self.buffer) <= 0:
                        break
                    data += self.buffer
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

        self.buffer += data

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

    def set_keep_alive_call(self):
        self.last_keep_alive_time = time()

    def get_last_keep_alive_call(self):
        return time() - self.last_keep_alive_time

    def get_message(self):
        """Determine message type and return it"""
        while len(self.buffer) > 4 and self.healthy:
            if not self.handshake_provided and self._handle_handshake():
                continue
            if self._handle_keep_alive():
                continue

            payload_length, = unpack(">I", self.buffer[:4])
            total_length = payload_length + 4

            if len(self.buffer) < total_length:
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

    def am_choking(self):
        return self.states['am_choking']

    def am_unchoking(self):
        return not self.states['am_choking']

    def is_choking(self):
        return self.states['peer_choking']

    def is_unchoking(self):
        return not self.states['peer_choking']

    def is_interested(self):
        return self.states['peer_interested']

    def am_interested(self):
        return self.states['am_interested']

    @staticmethod
    def __is_handshake(msg):
        return True if msg.startswith(b"\x13BitTorrent protocol") else False

    def _handle_handshake(self):
        try:
            msg = message.HandShake.from_bytes(self.buffer)
            self.handshake_provided = True
            print(f"Handshake_state for peer {self.ip_address}: {self.handshake_provided}")
            self.buffer = self.buffer[msg.total_length:]
            return True
        except Exception:
            self.healthy = False
        return False

    def handle_choke(self):
        self.states['peer_choking'] = True

    def handle_unchoke(self):
        self.states['peer_choking'] = False

    def handle_interested(self):
        self.states['peer_interested'] = True

        if self.am_choking():
            unchoke = message.Unchoke().to_bytes()
            self.send_message(unchoke)

    def handle_not_interested(self):
        self.states['peer_interested'] = False

    def handle_have(self, msg: message.Have):
        self.bitfield[msg.piece_index] = True

        if self.is_choking() and not self.am_interested():
            interested_msg = message.Interested().to_bytes()
            self.send_message(interested_msg)
            self.states['am_interested'] = True

    def handle_bitfield(self, msg: message.BitField):
        self.bitfield = msg.bitfield

        if self.is_choking() and not self.am_interested():
            interested_msg = message.Interested().to_bytes()
            self.send_message(interested_msg)
            print(f"Interested state changed for peer: {self.handshake_provided}")
            self.states['am_interested'] = True

    def handle_request(self, msg: message.Request):
        if self.is_interested() and self.is_unchoking():
            piece_index, block_offset, block_length = msg.piece_index, msg.block_offset, msg.block_length
            block = self.piece_manager.get_block(piece_index, block_offset, block_length)
            if block:
                piece = message.Piece(piece_index, block_offset, block_length, block).to_bytes()
                self.send_message(piece)
                logging.info(f"Sent piece index {msg.piece_index} to peer: {self.ip_address}")

    def handle_piece(self, msg: message.Piece):
        piece_index, block_offset, block = msg.piece_index, msg.block_offset, msg.block

        # handle case if piece is already downloaded
        if self.piece_manager.pieces[piece_index].is_full():
            return

        self.piece_manager.pieces[piece_index].set_block(block_offset, block)

        # handle case if all blocks in one piece are full
        if not self.piece_manager.pieces[piece_index].are_blocks_full():
            # more conditions for checking:
            # if piece is valid: try to encrypt with hash1 and compare with initial hash of the block
            if self.piece_manager.pieces[piece_index].write_piece():
                self.piece_manager.completed_pieces += 1

    def handle_cancel(self, msg: message.Cancel):
        piece_index = msg.piece_index
        piece = self.piece_manager.pieces[piece_index]
        # it's possible to cancel only pieces that are in PENDING status (currently downloading)
        # if piece is in FREE or FULL status -> do nothing
        if piece.state == State.PENDING:
            piece.state = State.FREE
            if piece.blocks is not []:
                piece.blocks = []
                logging.log(logging.INFO, f"Requesting was canceled for piece_hash: {piece.piece_hash}")

    def handle_port(self, msg: message.Port):
        port = msg.port
        if port:
            self.port = port
        logging.log(logging.INFO, "Port information was updated for peer: {self.ip_address}")

    def _handle_keep_alive(self):
        try:
            keep_alive = message.KeepAlive.from_bytes(self.read_buffer)
            logging.debug('handle_keep_alive - %s' % self.ip)
        except message.WrongMessageException:
            return False
        except Exception:
            return False

        self.read_buffer = self.read_buffer[keep_alive.total_length:]
        return True
