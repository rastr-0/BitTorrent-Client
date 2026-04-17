import mmap
import logging
from os.path import getsize
from threading import Thread

from bittorrent.constants import BLOCK_SIZE
from bittorrent.domain.block import State


class FileStorage(Thread):
    def __init__(self, piece_manager, file_path: str):
        super().__init__()
        self.piece_manager = piece_manager
        self.file_path = file_path

        self.file_length = piece_manager.total_pieces_length
        self.number_of_pieces = piece_manager.pieces_number
        self.piece_length = piece_manager.piece_length
        # Count actual total blocks — last piece has fewer blocks than a full piece
        self.total_blocks = sum(len(p.blocks) for p in piece_manager.pieces)
        self.saved_blocks = 0

        assert self.file_length != 0 and self.number_of_pieces != 0

        self._init_file()

    def run(self):
        while self.saved_blocks != self.total_blocks:
            for piece_index in range(self.number_of_pieces):
                self._write_block(piece_index)

    def _write_block(self, piece_index: int):
        for block_index, block in enumerate(self.piece_manager.pieces[piece_index].blocks):
            if block.state == State.FULL:
                piece_offset = piece_index * self.piece_length
                block_start = block_index * BLOCK_SIZE
                # Use actual block size — the last block in the last piece is smaller
                block_end = block_start + block.block_size

                try:
                    with open(self.file_path, "r+b") as file:
                        file_size = getsize(self.file_path)
                        with mmap.mmap(file.fileno(), length=file_size, access=mmap.ACCESS_WRITE) as mm:
                            mm[piece_offset + block_start:piece_offset + block_end] = block.data
                            mm.flush()
                            self.saved_blocks += 1
                except (OSError, ValueError, TypeError) as e:
                    logging.error(f"Error saving block {block_index} of piece {piece_index}: {e}")
                    return
                except Exception as e:
                    logging.error(f"Unexpected error saving block {block_index} of piece {piece_index}: {e}")
                    return

    def _init_file(self):
        """Pre-allocate the output file to the exact download size."""
        try:
            with open(self.file_path, "w+b") as file:
                file.write(b"\x00" * self.file_length)
        except (OSError, ValueError, TypeError) as e:
            logging.error(f"Error initializing file {self.file_path}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error initializing file {self.file_path}: {e}")
