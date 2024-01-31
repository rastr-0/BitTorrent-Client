from enum import Enum
from utilities import BLOCK_SIZE  # block_size --> 16KB
from time import time


class State(Enum):
    FREE = 0
    PENDING = 1  # number of pieces pending at a time is 5-7
    FULL = 2


class Block:
    def __init__(self, state=State.FREE, block_size=BLOCK_SIZE, data=b'', last_call=0):
        self.state = state
        self.block_size = block_size
        self.data = data
        self.last_call = last_call
