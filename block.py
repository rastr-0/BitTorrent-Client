from enum import Enum
from utilities import BLOCK_SIZE


class State(Enum):
    FREE = 0
    PENDING = 1
    FULL = 2


class Block(State):
    def __init__(self, state: State = State.FREE, block_size: int = BLOCK_SIZE, data: bytes = b''):
        self.state: State = state
        self.block_size = block_size
        self.data = data
