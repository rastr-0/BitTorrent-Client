import logging
from hashlib import sha1
import random
import string
from torrent import Torrent


def generate_client_id():
    # my bittorrent client identifier
    client_identifier = "RA1000"
    # random 18 bytes string
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    peer_id_not_decoded = f"-{client_identifier}-{random_string}"
    peer_id = sha1(peer_id_not_decoded.encode('utf-8')).digest()

    return peer_id


def get_pieces_number(torrent_file: Torrent):
    return torrent_file.number_of_pieces


BLOCK_SIZE = 2 ** 14  # 16KB
LOG = logging.getLogger('')
INFO_HASH = None
HANDSHAKE_PSTR = b"BitTorrent protocol"
LEN_HANDSHAKE_PSTR = len(HANDSHAKE_PSTR)
