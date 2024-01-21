from block import Block
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
        self.blocks: list[Block] = []
