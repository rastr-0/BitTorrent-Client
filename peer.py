import socket
import utilities
from time import time


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
        self.initial_communication_states = {
            "handshake_sent": False,
            "handshake_received": False,
            "bitfield_sent": False,
            "interested_sent": False,
        }
        self.buffer = b""
        # self.number_of_pieces = number_of_pieces
        # self.bitfield = bitstring.BitArray(number_of_pieces)

    def set_state(self, state, value=True):
        self.initial_communication_states[state] = value

    def get_state(self, state):
        return self.initial_communication_states.get(state, False)

    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip_address, self.port), timeout=2)
            self.socket.setblocking(False)
            self.healthy = True
            utilities.LOG.info(f"Connection with peer {self.ip_address} established")
            print(f"Connection to peer {self.ip_address} established")

        except TimeoutError:
            print(f"Failed to connect to peer {self.ip_address}")
            return False
        except ConnectionRefusedError:
            print(f"Connection to peer {self.ip_address} refused")
            return False
        except OSError as e:
            if "[Errno 113] No route to host" in str(e):
                print(f"No route to host for peer {self.ip_address}")
            else:
                print(f"OSError: {e}")
            return False

        return True

    def send_message(self, msg):
        self.healthy = False
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
