from torrent import Torrent
from peer_manager import PeerManager
from bcoding import bdecode


if __name__ == '__main__':

    torrent_file = 'debian-12.4.0.iso.torrent'

    torrent_object = Torrent()
    torrent_object.load_file(torrent_file)
    response = torrent_object.request_to_tracker()

    decoded_response = bdecode(response)
    peers_list = decoded_response['peers']

    manager = PeerManager()
    manager.connect_to_peers(peers_list)
