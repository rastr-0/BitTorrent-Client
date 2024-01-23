import logging

from block import Block, State
from math import ceil
from utilities import BLOCK_SIZE
from hashlib import sha1
import os


class Piece:
    def __init__(self, piece_index: int, piece_size: int, piece_hash: str):
        self.piece_index: int = piece_index
        self.piece_size: int = piece_size
        self.piece_hash: str = piece_hash
        self.raw_representation: bytes = b''
        self.piece_hash: str
        self.is_full: bool = False
        self.blocks_number: int = ceil(piece_size / BLOCK_SIZE)
        self.blocks: list[Block]

        self._init_blocks()

    def _init_blocks(self):
        self.blocks = []

        if self.blocks_number > 1:
            for i in range(self.blocks_number):
                self.blocks.append(Block())
        else:
            self.blocks.append(Block(block_size=self.piece_size))

    def are_blocks_full(self):
        for block in self.blocks:
            if block.state == State.FREE or block.state == State.PENDING:
                return False
        return True

    def get_block(self, block_offset, block_length):
        return self.raw_representation[block_offset:block_length]

    def set_block(self, offset, data):
        # index -> relative position of the block within the piece
        index = int(offset / BLOCK_SIZE)

        if not self.is_full and not self.blocks[index].state == State.FULL:
            self.blocks[index].data = data
            self.blocks[index].state = State.FULL

    def write_piece(self):
        # merge blocks to one piece
        data = self._merge_blocks()
        # check piece hash with original hash of the piece
        if not self._is_piece_valid(data):
            self._init_blocks()
            return False
        # NOT the best way for saving pieces. Must be reorganized!
        # create new dir (if doesn't exist) for pieces
        try:
            os.mkdir("downloaded_pieces")
        except Exception:
            logging.log(logging.INFO, "Directory exists")
        try:
            file_name = f"{sha1(data).digest()}_file"
            f = open(file_name, "wb")
            f.write(data)
            f.close()
        except FileExistsError:
            logging.log(logging.ERROR, "File for the piece already exists")

    def _is_piece_valid(self, data):
        """Compare merged blocks hash and original hash of the piece from tracker"""
        return sha1(data).digest() == self.piece_hash

    def _merge_blocks(self):
        """Since all blocks are full, they should be merged to one solid piece"""
        data = b''
        for block in self.blocks:
            data += block.data

        return data
