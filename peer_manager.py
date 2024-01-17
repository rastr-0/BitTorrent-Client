from peer import Peer
import message
import threading


class PeerManager:
    def __init__(self):
        self.connected_peers = []
        self.message = None
        self.lock = threading.Lock()

    def connect_to_peers(self, peers_list: list) -> None:
        """Establish TCP connection and do handshakes with peers"""
        print("The process of establishing connections and doing a handshakes started...")
        for peer in peers_list:
            peer_obj = Peer(peer['ip'], peer['port'])
            if peer_obj.connect():
                handshake_sent = peer_obj.handshake()
                handshake_received = peer_obj.process_handshake_response()
                if handshake_sent and handshake_received:
                    self.__add_peer(peer_obj)
        print("Here is the list of connected peers:")
        for connected_peer in self.connected_peers:
            print(f"ip: {connected_peer.ip_address}  port: {connected_peer.port}")

    def run(self):
        while True:
            pass

    def __process_message(self, new_msg: message.Message, peer: Peer):
        if isinstance(new_msg, message.Choke):
            peer.handle_choke(new_msg)
        elif isinstance(new_msg, message.Unchoke):
            peer.handle_unchoke(new_msg)
        elif isinstance(new_msg, message.Interested):
            peer.handle_interested(new_msg)
        elif isinstance(new_msg, message.NotInterested):
            peer.handle_not_interested(new_msg)
        elif isinstance(new_msg, message.Have):
            peer.handle_have(new_msg)

    def __add_peer(self, peer: Peer):
        with self.lock:
            self.connected_peers.append(peer)

    def send_keep_alive(self):
        for connected_peer in self.connected_peers:
            connected_peer.send_keep_alive()


