import utilities
from torrent import Torrent
from bcoding import bdecode


if __name__ == '__main__':

    torrent_file = 'debian-12.4.0.iso.torrent'

    # load .torrent file
    torrent_object = Torrent()
    torrent_object.load_file(torrent_file)

    # set utilities variables
    utilities.INFO_HASH = torrent_object.info_hash

    # decode the response
    response = torrent_object.request_to_tracker()
    decoded_response = bdecode(response)
    peers_list = decoded_response['peers']

    from peer_manager import PeerManager

    # create PeerManager object
    manager = PeerManager()
    # connect to peers and exchange handshakes with peers
    manager.connect_to_peers(peers_list)

    manager.test_send_interested()
    # handling incoming messages from the connected peers
    manager.run()

    manager.test_print_peers_buffer()

