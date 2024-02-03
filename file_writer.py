from threading import Thread
from utilities import BLOCK_SIZE, BLOCKS_IN_PIECE
from block import State
import os


class BlockSaver(Thread):
    def __init__(self, piece_manager):
        super().__init__()
        self.piece_manager = piece_manager
        self.file_length = self.piece_manager.total_pieces_length
        self.number_of_pieces = self.piece_manager.pieces_number
        self.piece_length = self.piece_manager.piece_length

        self.saved_blocks = 0

        assert self.file_length != 0 or self.number_of_pieces != 0

        self.file = self.allocate_space()

    def allocate_space(self):
        """Space is calculated in bytes.
            For each piece is allocated piece_length bytes in file.
            After each line with written piece should be 1 blank line for
            writing in the future its state (verified / not verified)"""

        piece_length = BLOCK_SIZE * BLOCKS_IN_PIECE
        total_space = (self.number_of_pieces-1) * piece_length
        # case for the last one piece which is, probably, shorter
        total_space += self.file_length - total_space

        file = os.open("downloaded_file", os.O_RDWR | os.O_CREAT)

        return file

    def run(self):
        while self.saved_blocks != self.number_of_pieces * BLOCKS_IN_PIECE:
            for piece_index in range(self.number_of_pieces.pieces):
                self._write_block(piece_index)

    def _write_block(self, piece_index):
        for block_index, block in enumerate(self.piece_manager.pieces.blocks):
            if block.state == State.FULL:
                piece_offset = piece_index * self.piece_length
                block_offset = block_index * BLOCK_SIZE

                os.truncate("downloaded_file", piece_offset + block_offset)
                os.write(self.file, block.data)

                self.saved_blocks += 1
