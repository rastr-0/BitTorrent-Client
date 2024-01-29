import utilities
from torrent import Torrent
from bcoding import bdecode
from piece_manager import PieceManager
import time
import message
from threading import Thread


# TODO: figure out the way to share instance variables of the PeerManager class between child and parent processes
#   Now the main problem is that pieces_handler works with the copy of PeerManager object
#   and connect_peers list is NOT updated

class RunBittorrent(Thread):
    def __init__(self, torrent_path):
        super().__init__()

        self.torrent = Torrent()
        self.torrent.load_file(torrent_path)

        self.pieces_manager = PieceManager(self.torrent)

        utilities.INFO_HASH = self.torrent.info_hash
        self.number_of_pieces = utilities.get_pieces_number(self.torrent)

        from peer_manager import PeerManager
        self.peer_manager = PeerManager(self.pieces_manager, self.number_of_pieces)

        peers_list = bdecode(self.torrent.request_to_tracker())['peers']

        self.peer_manager.connected_peers(peers_list)

        self.peer_manager.start()

    def run(self):
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

                piece_index, block_offset, block_length = data
                piece_request = message.Request(piece_index, block_offset, block_length).to_bytes()
                print(f"Request message: {piece_request} to peer: {peer_with_piece.ip_address}")
                peer_with_piece.send_message(piece_request)

            time.sleep(0.1)


def pieces_handler(piece_manager_param, peer_manager_param):
    # FIX: instance variables of the class are not updated properly
    #       Each process gets different copies of the object
    while not piece_manager_param.all_pieces_completed():
        if peer_manager_param.unchoked_peers_count() < 0:
            time.sleep(1.0)
            continue
        for piece in piece_manager_param.pieces:
            current_index = piece.piece_index

            if piece_manager_param.pieces[current_index].is_full:
                continue

            peer_with_piece = peer_manager_param.get_random_peer_with_piece(current_index)
            if not peer_with_piece:
                continue

            data = piece_manager_param.pieces[current_index].get_empty_block()
            if not data:
                continue

            piece_index, block_offset, block_length = data
            piece_request = message.Request(piece_index, block_offset, block_length).to_bytes()
            print(f"Request message: {piece_request} to peer: {peer_with_piece.ip_address}")
            peer_with_piece.send_message(piece_request)

        time.sleep(0.1)


if __name__ == '__main__':
    torrent_file = 'debian-12.4.0.iso.torrent'

    # Since PeerManager is a subclass of Thread,
    # start function calls run method of the class
    peer_manager.start()

