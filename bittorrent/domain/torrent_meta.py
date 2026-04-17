from bcoding import bencode, bdecode
from hashlib import sha1
import math

CLIENT_ID = b"-RS3154-1234abcdEFGH"


class TorrentMeta:
    """Parses a .torrent file and exposes metadata. No network I/O."""

    def __init__(self):
        self.announce_list: list = []
        self.info_hash: bytes = b""
        self.peer_id: bytes = CLIENT_ID
        self.file_size: int = 0
        self.pieces_hash: bytes = b""
        self.piece_length: int = 0
        self.number_of_pieces: int = 0
        self._filename: str = ""

    def load_file(self, file: str) -> None:
        with open(file, mode='rb') as binary_file:
            content = bdecode(binary_file)

        self.piece_length = content['info']['piece length']
        self.pieces_hash = content['info']['pieces']
        self.file_size = content['info']['length']
        raw_info_hash = bencode(content['info'])
        self.info_hash = sha1(raw_info_hash).digest()
        self.number_of_pieces = math.ceil(self.file_size / self.piece_length)
        self.announce_list = self._get_trackers(content)
        self._filename = content['info']['name']

    def get_filename(self) -> str:
        return self._filename

    @staticmethod
    def _get_trackers(decoded_file: dict) -> list:
        if 'announce_list' in decoded_file:
            return decoded_file['announce-list']
        return [[decoded_file['announce']]]
