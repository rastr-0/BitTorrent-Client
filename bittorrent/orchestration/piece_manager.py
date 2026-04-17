import bitstring

from bittorrent.domain.block import State
from bittorrent.domain.piece import Piece


class PieceManager:
    def __init__(self, meta):
        self.pieces_number = meta.number_of_pieces
        self.pieces_hash = meta.pieces_hash
        self.piece_length = meta.piece_length
        self.total_pieces_length = meta.file_size

        self.completed_pieces = 0
        self.bitfield = bitstring.BitArray(self.pieces_number)
        self.pieces = self._init_pieces()

    def _init_pieces(self):
        pieces = []

        for i in range(self.pieces_number - 1):
            start = i * 20
            pieces.append(Piece(i, self.piece_length, self.pieces_hash[start:start + 20]))

        # Last piece uses its own correct hash slice and may be shorter than piece_length
        last_start = (self.pieces_number - 1) * 20
        last_length = self.total_pieces_length - (self.pieces_number - 1) * self.piece_length
        pieces.append(
            Piece(self.pieces_number - 1, last_length, self.pieces_hash[last_start:last_start + 20])
        )

        return pieces

    def get_block(self, piece_index, block_offset, block_length):
        for piece in self.pieces:
            if piece_index == piece.piece_index:
                if piece.is_full:
                    return piece.get_block(block_offset, block_length)
                break
        return None

    def all_pieces_completed(self):
        return all(piece.is_full for piece in self.pieces)

    def receive_block(self, piece_index, piece_offset, piece_data):
        if self.pieces[piece_index].is_full:
            return

        self.pieces[piece_index].set_block(piece_offset, piece_data)
        if self.pieces[piece_index].are_blocks_full():
            if self.pieces[piece_index].verify_piece():
                self.update_bitfield(piece_index)
                self.completed_pieces += 1

    def number_of_full_blocks(self, piece_index):
        return sum(1 for block in self.pieces[piece_index].blocks if block.state == State.FULL)

    def update_bitfield(self, piece_index):
        self.bitfield[piece_index] = 1
