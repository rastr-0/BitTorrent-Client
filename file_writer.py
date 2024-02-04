from threading import Thread
from utilities import BLOCK_SIZE, BLOCKS_IN_PIECE
from block import State
import mmap
from os.path import getsize


class BlockSaver(Thread):
    def __init__(self, piece_manager, file_path):
        super().__init__()
        self.piece_manager = piece_manager
        self.file_length = self.piece_manager.total_pieces_length
        self.number_of_pieces = self.piece_manager.pieces_number
        self.piece_length = self.piece_manager.piece_length

        self.saved_blocks = 0

        assert self.file_length != 0 or self.number_of_pieces != 0

        self.file_path = file_path
        self._init_file(self.file_path)

    def run(self):
        while self.saved_blocks != self.number_of_pieces * BLOCKS_IN_PIECE:
            for piece_index in range(self.number_of_pieces):
                self._write_block(piece_index)

    def _write_block(self, piece_index):
        """This function calculates starting point and offsets for writing block to the right position"""
        for block_index, block in enumerate(self.piece_manager.pieces[piece_index].blocks):
            if block.state == State.FULL:
                piece_offset = piece_index * self.piece_length
                block_start = block_index * BLOCK_SIZE
                block_offset = block_start + BLOCK_SIZE

                try:
                    with open(self.file_path, "r+b") as file:
                        # os.path function
                        file_size = getsize(self.file_path)
                        with mmap.mmap(file.fileno(), length=file_size, access=mmap.ACCESS_WRITE) as mmap_file:
                            mmap_file[piece_offset+block_start:piece_offset+block_offset] = block.data
                            mmap_file.flush()
                            self.saved_blocks += 1
                except (OSError, ValueError, TypeError) as e:
                    print(f"Error: {e} while saving block occurred")
                    return
                except Exception as e:
                    print(f"Unexpected error: {e} while saving block occurred")
                    return

    def verify_pieces(self):
        """Logic for comparing hashes of downloaded pieces with original hashes"""
        pass

    def _init_file(self, file_path):
        """Initialize file with empty line sufficient for storing all pieces"""
        piece_length = BLOCK_SIZE * BLOCKS_IN_PIECE
        total_space = (self.number_of_pieces - 1) * piece_length
        # case for the last piece which can be shorter
        total_space += min(piece_length, self.file_length - total_space)
        try:
            with open(file_path, "w+b") as file:
                file.write(b"1" * total_space)
        except (OSError, ValueError, TypeError) as e:
            print(f"Error: {e} while initializing a file")
            return
        except Exception as e:
            print(f"Unexpected error: {e} while initializing a file")
            return
