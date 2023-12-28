# bencode -> decoding
# bdecode -> encoding
from bcoding import bencode, bdecode
from hashlib import sha1
import random
import string
import requests


class Torrent:
    def __init__(self):
        self.decoded_file = {}
        self.announce_list = []
        self.info_hash = str()
        # peer_id is generated in Azureus-style
        self.peer_id = str()
        self.port: int = 0
        self.uploaded: int = 0
        self.downloaded: int = 0
        self.left: int = 0
        self.event = str()
        self.file_size: int = 0
        self.piece_length: int = 0
        # self.number_of_pieces: int = 0

    def load_file(self, file):
        with open(file, mode='rb') as binary_file:
            content = bdecode(binary_file)

        self.decoded_file = content
        self.piece_length = self.decoded_file['info']['piece length']
        self.file_size = self.decoded_file['info']['length']
        self.event = 'started'
        self.uploaded = 0
        self.downloaded = 0
        self.left = self.file_size
        raw_info_hash = bencode(self.decoded_file['info'])
        self.info_hash = sha1(raw_info_hash).digest()
        # my bittorrent client identifier
        client_identifier = 'RA1000'
        # random 18 bytes string
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        peer_id_not_decoded = f"-{client_identifier}-{random_string}"
        self.peer_id = sha1(peer_id_not_decoded.encode('utf-8')).digest()
        self.port = 6881
        self.announce_list = self.__get_trackers()

        return self

    def __get_trackers(self):
        # handle multi-file structure
        if 'announce_list' in self.decoded_file:
            return self.decoded_file['announce-list']
        # handle single-file structure
        else:
            return [[self.decoded_file['announce']]]

    def request_to_tracker(self):
        params = {
            "info_hash": self.info_hash,
            "peer_id": self.peer_id,
            "port": self.port,
            "uploaded": self.uploaded,
            "downloaded": self.downloaded,
            "left": self.left,
            "event": self.event
        }

        tracker_response = requests.get(self.announce_list[0][0], params=params, verify=False)
        if tracker_response:
            return tracker_response.text
        else:
            return "Error occurs"


torrent_file = 'debian-12.4.0.iso.torrent'

torrent_object = Torrent()
torrent_object.load_file(torrent_file)
response = torrent_object.request_to_tracker()

print(response)
