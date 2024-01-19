import logging
import select

from peer import Peer
import message
import threading
import errno


class PeerManager:
    def __init__(self, number_of_pieces=-1):
        self.connected_peers = []
        self.message = None
        self.lock = threading.Lock()
        self.active = True
        self.number_of_pieces = number_of_pieces

    def connect_to_peers(self, peers_list: list) -> None:
        """Establish TCP connection and do handshakes with peers"""
        print("The process of establishing connections and doing a handshakes started...")
        for peer in peers_list:
            peer_obj = Peer(self.number_of_pieces, peer['ip'], peer['port'])
            if peer_obj.connect():
                handshake_sent = peer_obj.handshake()
                handshake_received = peer_obj.process_handshake_response()
                if handshake_sent and handshake_received:
                    self.__add_peer(peer_obj)
        print("Here is the list of connected peers:")
        for connected_peer in self.connected_peers:
            print(f"ip: {connected_peer.ip_address}  port: {connected_peer.port}")

    @staticmethod
    def __read_buffer_from_socket(socket):
        """Get data from the socket and return them in a byte-string format"""
        buffer_size = 4096  # 2^12
        data = b''
        socket.setblocking(False)
        while True:
            try:
                ready_to_read, _, _ = select.select([socket], [], [], 1)
                buffer = b''
                if ready_to_read:
                    buffer = socket.recv(buffer_size)
                if len(buffer) <= 0:
                    break
                data += buffer
            except socket.error as e:
                # buffer is empty
                if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                    pass
                else:
                    print(f"Socket-related error occur: ({e.args[0]}) while reading "
                          f"a buffer for the following socket: {socket}")
            except BufferError:
                logging.exception(f"Error occur while reading a buffer for following socket: {socket}")

        return data

    def run(self):
        """High-level messages handling function
        1 - Get ready for reading sockets of the connected peers
        2 - Get peers based on the sockets
        3 - Get payload of the incoming message by reading buffer from socket
        4 - Add payload data to the peers buffers
        """
        while self.active:
            payload = b""

            for peer in self.connected_peers:
                try:
                    payload = peer.read_buffer()
                except Exception:
                    logging.error(f"Error occur while reading socket "
                                  f"for the peer with following ip: {peer.ip_address} and port: {peer.port}")
                for peer_message in peer.get_message(payload):
                    self.__process_message(peer_message, peer)

    @staticmethod
    def __process_message(new_msg: message.Message, peer: Peer):
        """Based on the message type is called handling function"""
        if isinstance(new_msg, message.Choke):
            peer.handle_choke()
        elif isinstance(new_msg, message.Unchoke):
            peer.handle_unchoke()
        elif isinstance(new_msg, message.Interested):
            peer.handle_interested()
        elif isinstance(new_msg, message.NotInterested):
            peer.handle_not_interested()
        elif isinstance(new_msg, message.Have):
            peer.handle_have(new_msg)
        elif isinstance(new_msg, message.BitField):
            peer.handle_bitfield(new_msg)

    def __add_peer(self, peer: Peer):
        with self.lock:
            self.connected_peers.append(peer)
            peer.healthy = True

    def send_keep_alive(self):
        keep_alive_message = message.KeepAlive().to_bytes()
        for connected_peer in self.connected_peers:
            connected_peer.send_message(keep_alive_message)

    def get_peer_by_socket(self, socket):
        for peer in self.connected_peers:
            if socket == peer.socket:
                return peer

        raise Exception("Peer has not been found")

    def test_send_interested(self):
        interested_message = message.Interested().to_bytes()
        for peer in self.connected_peers:
            peer.send_message(interested_message)

    def test_send_unchoke(self):
        unchoke_message = message.Unchoke().to_bytes()
        for peer in self.connected_peers:
            peer.send_message(unchoke_message)

    def test_print_peers_buffer(self):
        for peer in self.connected_peers:
            print(peer.buffer)
