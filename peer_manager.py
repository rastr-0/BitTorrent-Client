import errno

from peer import Peer
from message import HandShake
from utilities import INFO_HASH, PEER_ID
import socket


class PeerManager:
    def __init__(self):
        self.connected_peers = []
        self.message = None

    def connect_to_peers(self, peers_list: list) -> None:
        """Establish TCP connection with peers"""
        for peer in peers_list:
            peer_obj = Peer(peer['ip'], peer['port'])
            if peer_obj.connect():
                self.connected_peers.append(peer_obj)
        for connected_peer in self.connected_peers:
            print(f"ip: {connected_peer.ip_address}  port: {connected_peer.port}")

    @staticmethod
    def __handshake(peer):
        if peer.socket is None:
            return False
        try:
            handshake = HandShake(info_hash=INFO_HASH, peer_id=PEER_ID).to_bytes()
            peer.send_message(msg=handshake)
            print(f"HandShake was sent to user with following ip: {peer.ip_address} and port: {peer.port}")
            # LOG.log(f"HandShake was sent to user with following ip: {peer.ip_address}")
            return True
        except ConnectionError:
            print(f"HandShake was not sent to user with following ip: {peer.ip_address} and port: {peer.port}")
            # LOG.exception(f"HandShake was not sent to user with following ip: {peer.ip_address}")
        return False

    def initiate_handshake(self):
        """Send Handshake to peers and change handshake_sent state"""
        for connected_peer in self.connected_peers:
            if not connected_peer.get_state("handshake_sent"):
                if self.__handshake(connected_peer):
                    connected_peer.set_state("handshake_sent")
                else:
                    pass

    def receive_handshake(self):
        """Handle Handshake from the peers and change handshake_received state"""
        for connected_peer in self.connected_peers:
            if connected_peer.get_state("handshake_sent"):
                # call response data handling function
                self.process_buffer(connected_peer)
                connected_peer.set_state("handshake_received")

    @staticmethod
    def __read_buffer(_socket):
        data = b""
        # parameter for socket.recv function should be small power of 2 -> 4096 (2^12)
        buffer_size = 4096
        while True:
            try:
                buffer = _socket.recv(buffer_size)
                if len(buffer) <= 0:
                    break
                data += buffer
            except socket.error as e:
                # buffer is empty
                if e.args[0] == errno.EAGAIN or e.args[0] == errno.EWOULDBLOCK:
                    pass
                else:
                    print(f"Socket-related error occur: ({e.args[0]}) while reading "
                          f"a buffer for the following socket: {_socket}")
                    break
            except BufferError:
                print(f"BufferError occur while reading a buffer "
                      f"for the following socket: {_socket}")
                break
        return data

    def process_buffer(self, connected_peer):
        """Get peers socket, pass socket to _read_buffer handle data by types of messages"""
        peer_socket = connected_peer.socket
        response_message = self.__read_buffer(peer_socket)
        # handle type of message

    def determine_message_type(self, response_data):
        pass

    def send_messages_to_peers(self, peers_list: list) -> None:
        """Stands for sending messages to peers"""
        pass
