import pubsub

from piece import Piece
from utilities import get_pieces_hash, get_pieces_number, get_piece_length, get_torrent_total_length
import bitstring
from pubsub import pub


class PieceManager:
    def __init__(self, torrent_object):
        self.pieces_number = get_pieces_number(torrent_object)
        self.pieces_hash = get_pieces_hash(torrent_object)
        self.piece_length = get_piece_length(torrent_object)
        self.total_pieces_length = get_torrent_total_length(torrent_object)

        self.completed_pieces = 0
        self.bitfield = bitstring.BitArray(self.pieces_number)
        self.pieces = self._init_pieces()

        pub.subscribe(self.receive_block, "ReceiveBlock")
        pub.subscribe(self.update_bitfield, "PieceCompleted")

    def _init_pieces(self):
        pieces = []
        start_index, end_index = 0, 0

        # all pieces, except the last one: can be shorter than others
        for i in range(self.pieces_number - 1):
            # length of each piece_hash is 20 bytes
            start_index = i * 20
            end_index = start_index + 20
            pieces.append(Piece(i, self.piece_length, self.pieces_hash[start_index:end_index]))

        # the last one piece case
        last_piece_length = self.total_pieces_length - (self.pieces_number - 1) * self.piece_length
        pieces.append(Piece(self.pieces_number - 1, last_piece_length, self.pieces_hash[start_index:end_index]))

        return pieces

    def get_block(self, piece_index, block_offset, block_length):
        for piece in self.pieces:
            if piece_index == piece.piece_index:
                if piece.is_full:
                    return piece.get_block(block_offset, block_length)
                else:
                    break

        return None

    def all_pieces_completed(self):
        for piece in self.pieces:
            if not piece.is_full:
                return False
        return True

    def receive_block(self, data):
        piece_index, piece_offset, piece_data = data

        if self.pieces[piece_index].is_full:
            return

        self.pieces[piece_index].set_block(piece_offset, piece_data)

        if self.pieces[piece_index].are_blocks_full():
            if self.pieces[piece_index].verify_piece():
                self.completed_pieces += 1

    def update_bitfield(self, piece_index):
        self.bitfield[piece_index] = 1



