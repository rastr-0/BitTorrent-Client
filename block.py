from enum import Enum
from utilities import BLOCK_SIZE  # block_size --> 16KB


class State(Enum):
    FREE = 0
    PENDING = 1
    FULL = 2


class Block:
    def __init__(self, state=State.FREE, block_size=BLOCK_SIZE, data=b''):
        self.state = state
        self.block_size = block_size
        self.data = data
