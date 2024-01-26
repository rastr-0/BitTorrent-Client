import utilities
from torrent import Torrent
from bcoding import bdecode
from piece_manager import PieceManager
import time
import message
import multiprocessing
from multiprocessing.managers import BaseManager


class MultiManager(BaseManager):
    pass

# TODO: figure out the way to share instance variables of the PeerManager class between child and parent processes
#   Now the main problem is that pieces_handler works with the copy of PeerManager object
#   and connect_peers list is NOT updated


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

    # load .torrent file
    torrent_object = Torrent()
    torrent_object.load_file(torrent_file)

    # number of pieces in the .torrent file
    number_of_pieces = utilities.get_pieces_number(torrent_object)

    # set utilities variables
    utilities.INFO_HASH = torrent_object.info_hash

    # decode the response from the tracker
    response = torrent_object.request_to_tracker()
    decoded_response = bdecode(response)
    peers_list = decoded_response['peers']

    from peer_manager import PeerManager
    # create PieceManager object
    piece_manager = PieceManager(torrent_object)

    # create PeerManager object
    peer_manager = PeerManager(piece_manager, number_of_pieces)

    # register classes objects with BaseManager
    MultiManager.register()

    # connect to peers and exchange handshakes with peers
    peer_manager.connect_to_peers(peers_list)

    # Since PeerManager is a subclass of Thread,
    # start function calls run method of the class
    peer_manager.start()

    # handling sending requests
    time.sleep(30.0)
    pieces_handler = multiprocessing.Process(target=pieces_handler, args=(piece_manager, peer_manager))
    pieces_handler.start()
    pieces_handler.join()
