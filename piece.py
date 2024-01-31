import logging

from block import Block, State
from math import ceil
from utilities import BLOCK_SIZE
from hashlib import sha1
import os
from time import time
from pubsub import pub


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

            # condition checks if there is a last block with non-standard size in the last piece
            if (self.piece_size % BLOCK_SIZE) > 0:
                # if so, set size of this block to the remaining data
                self.blocks[self.blocks_number - 1].block_size = self.piece_size % BLOCK_SIZE

        else:
            self.blocks.append(Block(block_size=self.piece_size))

    def are_blocks_full(self):
        for block in self.blocks:
            if block.state == State.FREE or block.state == State.PENDING:
                return False
        return True

    def get_empty_block(self):
        # TODO: Implement rarest_piece logic for choosing free blocks
        """Finds a free block for requesting data from peers
            Returns:
                Tuple[int, int, int] -> (piece_index, block_offset, block_size) if block is FREE,
                otherwise returns None"""
        if self.is_full:
            return None
        for block_index, block in enumerate(self.blocks):
            if block.state == State.FREE:
                self.blocks[block_index].state = State.PENDING
                self.blocks[block_index].last_call = time()
                return self.piece_index, block_index * BLOCK_SIZE, block.block_size
        return None

    def set_block(self, piece_offset, data):
        piece_index = int(piece_offset / BLOCK_SIZE)

        if not self.is_full and not self.blocks[piece_index].state == State.FULL:
            self.blocks[piece_index].data = data
            self.blocks[piece_index].state = State.FULL

    def get_block(self, block_offset, block_length):
        return self.raw_representation[block_offset:block_length]

    def update_block_status(self):
        """Updates block states that were requested but never sent"""
        for i, block in enumerate(self.blocks):
            if block.state == State.PENDING and (time() - block.last_call) > 5:
                self.blocks[i] = Block()

    def verify_piece(self):
        """Verify piece and writes data to disk"""
        piece = self.__merge_blocks()
        if not self.__valid_piece(piece):
            self._init_blocks()
            return False

        self.is_full = True
        self.raw_representation = piece

        pub.sendMessage("PieceCompleted", piece_index=self.piece_index)

        return True

    def __merge_blocks(self):
        """Merges all blocks data to a single solid piece"""
        buffer = b""

        for block in self.blocks:
            buffer += block.data

        return buffer

    def __valid_piece(self, data):
        """Checks hash of a piece from the tracker response with the hash of merged blocks"""
        hash_merged_blocks = sha1(data).digest()
        if hash_merged_blocks == self.piece_hash:
            return True
        return False
