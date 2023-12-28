from peer import Peer


class PeerManager:
    def __init__(self):
        self.connected_peers = []

    def connect_to_peers(self, peers_list) -> None:
        for peer in peers_list:
            peer_obj = Peer(peer['ip'], peer['port'])
            peer_obj.connect()
            self.connected_peers.append(peer_obj)
        for connected_peer in self.connected_peers:
            print(f"ip: {connected_peer.ip_address}  port: {connected_peer.port}")


