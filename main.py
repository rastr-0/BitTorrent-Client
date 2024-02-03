import utilities
from torrent import Torrent
from bcoding import bdecode
from piece_manager import PieceManager
import time
import message
from threading import Thread
from block import State
from file_writer import BlockSaver


# TODO: implement logic for allocating space in result file
#  and saving already downloaded blocks to the right place in the file
#  blocks saving logic can be run in another Thread with usage of mmap

class RunBittorrent(Thread):
    def __init__(self, torrent_path):
        super().__init__()
        self.completed_blocks_number = 0
        self.completed_percentage = 0

        self.torrent = Torrent()
        self.torrent.load_file(torrent_path)

        self.file_length = utilities.get_torrent_total_length(self.torrent)

        self.pieces_manager = PieceManager(self.torrent)
        # self.blocks_writer = BlockSaver(self.pieces_manager)

        utilities.INFO_HASH = self.torrent.info_hash
        self.number_of_pieces = utilities.get_pieces_number(self.torrent)

        from peer_manager import PeerManager
        self.peer_manager = PeerManager(self.pieces_manager, self.number_of_pieces)

        peers_list = bdecode(self.torrent.request_to_tracker())['peers']

        self.peer_manager.connect_to_peers(peers_list)

        # running functions in threads
        self.peer_manager.start()
        # self.blocks_writer.start()

    def run(self):
        # wait for the peers do initials steps, needs to be implemented other way
        time.sleep(7.0)

        while not self.pieces_manager.all_pieces_completed():
            if self.peer_manager.unchoked_peers_count() < 0:
                time.sleep(1.0)
                continue
            for piece in self.pieces_manager.pieces:
                current_index = piece.piece_index

                if self.pieces_manager.pieces[current_index].is_full:
                    continue

                peer_with_piece = self.peer_manager.get_random_peer_with_piece(current_index)
                if not peer_with_piece:
                    continue

                data = self.pieces_manager.pieces[current_index].get_empty_block()
                if not data:
                    continue

                self.pieces_manager.pieces[current_index].update_block_status()

                piece_index, block_offset, block_length = data
                piece_request = message.Request(piece_index, block_offset, block_length).to_bytes()
                if peer_with_piece is not None:
                    if not peer_with_piece.healthy:
                        self.peer_manager.disconnect_peer(peer_with_piece)
                    peer_with_piece.send_message(piece_request)
                    time.sleep(0.1)

                self.display_downloading_process()

    def display_downloading_process(self):
        blocks_completed = 0

        for i, piece in enumerate(self.pieces_manager.pieces):
            blocks_completed += sum(1 for block in piece.blocks if block.state == State.FULL)

        if blocks_completed > 0 and blocks_completed != self.completed_blocks_number:
            self.completed_blocks_number = blocks_completed
            percentage = round((self.completed_blocks_number // 16 * 100) / self.number_of_pieces, 2)
            if percentage != self.completed_percentage:
                self.completed_percentage = percentage
                print(f"Downloaded {self.completed_percentage} %")


if __name__ == '__main__':
    torrent_file = 'debian-12.4.0-amd64-netinst.iso.torrent'

    bittorrent = RunBittorrent(torrent_file)
    bittorrent.start()
