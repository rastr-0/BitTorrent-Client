from typing import Protocol


class StorageProtocol(Protocol):
    """Interface for writing downloaded blocks to persistent storage."""

    def write_block(self, piece_index: int, block_offset: int, data: bytes) -> None: ...

    def close(self) -> None: ...
