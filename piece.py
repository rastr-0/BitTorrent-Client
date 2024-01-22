from block import Block, State
from math import ceil
from utilities import BLOCK_SIZE


class Piece:
    def __init__(self, piece_index: int, piece_size: int, piece_hash: str):
        self.piece_index: int = piece_index
        self.piece_size: int = piece_size
        self.piece_hash: str = piece_hash
        self.raw_representation: bytes = b''
        self.piece_hash: str
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
