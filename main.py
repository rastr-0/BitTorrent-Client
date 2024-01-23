import utilities
from torrent import Torrent
from bcoding import bdecode
from piece_manager import PieceManager


# DONE: Implemented basic logic for Piece and PieceManager classes
#       Added 2 new classes in message.py -> Request and Piece
# TODO: Implement logic for handling request and piece messages

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
    manager = PeerManager(piece_manager, number_of_pieces)
    # connect to peers and exchange handshakes with peers
    manager.connect_to_peers(peers_list)

    manager.test_send_interested()
    # handling incoming messages from the connected peers
    manager.run()
