import logging
from torrent import Torrent
from bittorrent.constants import BLOCK_SIZE, BLOCKS_IN_PIECE, HANDSHAKE_PSTR, LEN_HANDSHAKE_PSTR


def get_pieces_number(torrent_file: Torrent):
    return torrent_file.number_of_pieces


def get_pieces_hash(torrent_file: Torrent):
    return torrent_file.pieces_hash


def get_torrent_total_length(torrent_file: Torrent):
    return torrent_file.file_size


def get_piece_length(torrent_file: Torrent):
    return torrent_file.piece_length


LOG = logging.getLogger('')
INFO_HASH = None
