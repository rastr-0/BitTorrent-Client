import logging
from torrent import Torrent


def get_pieces_number(torrent_file: Torrent):
    return torrent_file.number_of_pieces


def get_pieces_hash(torrent_file: Torrent):
    return torrent_file.pieces_hash


def get_torrent_total_length(torrent_file: Torrent):
    return torrent_file.file_size


def get_piece_length(torrent_file: Torrent):
    return torrent_file.piece_length


BLOCK_SIZE = 2 ** 14  # 16KB
BLOCKS_IN_PIECE = 16
LOG = logging.getLogger('')
INFO_HASH = None
HANDSHAKE_PSTR = b"BitTorrent protocol"
LEN_HANDSHAKE_PSTR = len(HANDSHAKE_PSTR)
