import socket
from utilities import LOG


class Peer:
    def __init__(self, ip, port=6881):
        self.states = {
            'peer_choking': True,
            'peer_interested': False
        }
        self.ip_address = ip
        self.port = port
        self.socket = None
        # self.number_of_pieces = number_of_pieces
        # self.bitfield = bitstring.BitArray(number_of_pieces)

    def connect(self):
        try:
            self.socket = socket.create_connection((self.ip_address, self.port), timeout=2)
            self.socket.setblocking(False)
            LOG.info(f"Connection with peer {self.ip_address} established")
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

    def send_handshake(self):
        pass



