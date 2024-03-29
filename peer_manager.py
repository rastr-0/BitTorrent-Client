import logging
from threading import Thread
from pubsub import pub

from peer import Peer
import message
import threading
from random import choice


class PeerManager(Thread):
    def __init__(self, piece_manager, number_of_pieces=-1):
        Thread.__init__(self)

        self.piece_manager = piece_manager

        self.connected_peers = []
        self.message = None
        self.lock = threading.Lock()
        self.active = True
        self.number_of_pieces = number_of_pieces

        pub.subscribe(self.request_of_piece, "PieceRequestFromPeer")

    def get_random_peer_with_piece(self, piece_index):
        peers_having_piece = []
        for peer in self.connected_peers:
            if peer.handshake_provided:
                if peer.has_piece(piece_index) and peer.is_unchoking() and peer.am_interested():
                    peers_having_piece.append(peer)
        if peers_having_piece:
            return choice(peers_having_piece)
        return None

    def connect_to_peers(self, peers_list: list) -> None:
        """Establish TCP connection and do handshakes with peers"""
        print("The process of establishing connections and doing a handshakes started...")
        for peer in peers_list:
            peer_obj = Peer(self.piece_manager, self.number_of_pieces, peer['ip'], peer['port'])
            if peer_obj.connect():
                handshake_sent = peer_obj.handshake()
                if handshake_sent:
                    self.__add_peer(peer_obj)
        print("Here is the list of connected peers:")
        for connected_peer in self.connected_peers:
            print(f"ip: {connected_peer.ip_address}  port: {connected_peer.port}")

    def run(self):
        """High-level messages handling function
        1 - Get ready for reading sockets of the connected peers
        2 - Get peers based on the sockets
        3 - Get payload of the incoming message by reading buffer from socket
        4 - Add payload data to the peers buffers
        """
        while self.active:
            for peer in self.connected_peers:
                try:
                    peer.read_buffer()
                except Exception:
                    logging.error(f"Error occurred while reading socket "
                                  f"for the peer with following ip: {peer.ip_address} and port: {peer.port}")
                    self.disconnect_peer(peer)

                for peer_message in peer.get_messages():
                    self.__process_message(peer_message, peer)

    @staticmethod
    def __process_message(new_msg: message.Message, peer: Peer):
        """For each incoming message is called specific handling function"""
        if isinstance(new_msg, message.Choke):
            # print(f"Get a Choke message from peer: {peer.ip_address}")
            peer.handle_choke()
        elif isinstance(new_msg, message.Unchoke):
            # print(f"Get a UnChoke message from peer: {peer.ip_address}")
            peer.handle_unchoke()
        elif isinstance(new_msg, message.Interested):
            # print(f"Get a Interested message from peer: {peer.ip_address}")
            peer.handle_interested()
        elif isinstance(new_msg, message.NotInterested):
            # print(f"Get a NotInterested message from peer: {peer.ip_address}")
            peer.handle_not_interested()
        elif isinstance(new_msg, message.Have):
            # print(f"Get a Have message from peer: {peer.ip_address}")
            peer.handle_have(new_msg)
        elif isinstance(new_msg, message.BitField):
            # print(f"Get a BitField message from peer: {peer.ip_address}")
            peer.handle_bitfield(new_msg)
        elif isinstance(new_msg, message.Request):
            # print(f"Get a Request message from peer: {peer.ip_address}")
            peer.handle_request(new_msg)
        elif isinstance(new_msg, message.Piece):
            # print(f"Got a part of Piece from peer: {peer.ip_address}")
            peer.handle_piece(new_msg)
        elif isinstance(new_msg, message.Cancel):
            # print(f"Get a Cancel message from peer: {peer.ip_address}")
            peer.handle_cancel(new_msg)
        elif isinstance(new_msg, message.Port):
            # print(f"Get a Port message from peer: {peer.ip_address}")
            # functionality is not implemented for handle_port
            peer.handle_port()

    def __add_peer(self, peer: Peer):
        with self.lock:
            self.connected_peers.append(peer)
            peer.healthy = True

    def unchoked_peers_count(self):
        count = 0
        for peer in self.connected_peers:
            if peer.is_unchoking():
                count += 1
        return count

    def disconnect_peer(self, peer):
        if peer in self.connected_peers:
            try:
                peer.socket.close()
            except ConnectionRefusedError or ConnectionError:
                logging.log(logging.ERROR, "Unable to establish connection with peer: {peer.ip_address} : {peer.port}")
            self.connected_peers.remove(peer)

    def request_of_piece(self, request=None, peer=None):
        if not request or not peer:
            return
        piece_index, block_offset, block_length = request.piece_index, request.block_offset, request.block_length

        block = self.piece_manager.get_block(piece_index, block_offset, block_length)

        if block:
            piece_msg = message.Piece(piece_index, block_offset, block_length, block).to_bytes()
            peer.send_message(piece_msg)
