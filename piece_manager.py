from piece import Piece
from utilities import get_pieces_hash, get_pieces_number, get_piece_length, get_torrent_total_length
import bitstring


class PieceManager:
    def __init__(self, torrent_object):
        self.pieces_number = get_pieces_number(torrent_object)
        self.pieces_hash = get_pieces_hash(torrent_object)
        self.piece_length = get_piece_length(torrent_object)
        self.total_pieces_length = get_torrent_total_length(torrent_object)

        self.complete_pieces = 0
        self.bitfield = bitstring.BitArray(self.pieces_number)
        self.pieces = self._init_pieces()

    def _init_pieces(self):
        pieces = []
        start_index, end_index = 0, 0

        # all pieces, except the last one: can be shorter than others
        for i in range(self.pieces_number - 1):
            # length of each piece_hash is 20 bytes
            start_index = i*20
            end_index = start_index+20
            pieces.append(Piece(i, self.piece_length, self.pieces_hash[start_index:end_index]))

        # the last one piece case
        last_piece_length = self.total_pieces_length - (self.pieces_number - 1) * self.piece_length
        pieces.append(Piece(self.pieces_number-1, last_piece_length, self.pieces_hash[start_index:end_index]))

        return pieces
