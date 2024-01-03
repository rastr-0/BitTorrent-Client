from peer import Peer
from message import HandShake
from utilities import INFO_HASH, PEER_ID, LOG


class PeerManager:
    def __init__(self):
        self.connected_peers = []
        self.handshaked_peers = []
        self.message = None

    @staticmethod
    def _handshake(peer):
        try:
            handshake = HandShake(info_hash=INFO_HASH, peer_id=PEER_ID).to_bytes()
            peer.send_message(msg=handshake)
            print(f"HandShake was sent to user with following ip: {peer.ip_address}")
            LOG.log(f"HandShake was sent to user with following ip: {peer.ip_address}")
            return True
        except ConnectionError:
            print(f"HandShake was not sent to user with following ip: {peer.ip_address}")
            LOG.exception(f"HandShake was not sent to user with following ip: {peer.ip_address}")
        return False

    def connect_to_peers(self, peers_list: list) -> None:
        for peer in peers_list:
            peer_obj = Peer(peer['ip'], peer['port'])
            peer_obj.connect()
            self.connected_peers.append(peer_obj)
        for connected_peer in self.connected_peers:
            print(f"ip: {connected_peer.ip_address}  port: {connected_peer.port}")

    def add_peers(self):
        for connected_peer in self.connected_peers:
            if self._handshake(connected_peer):
                self.handshaked_peers.append(connected_peer)
            else:
                pass

    def send_messages_to_peers(self, peers_list: list) -> None:
        """stands for sending messages to peers"""
        pass
