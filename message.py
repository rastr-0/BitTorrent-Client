from utilities import HANDSHAKE_PSTR, LEN_HANDSHAKE_PSTR
from struct import pack, unpack


class Message:
    def to_bytes(self):
        raise NotImplementedError()

    @classmethod
    def from_bytes(cls, payload):
        raise NotImplementedError()


class HandShake(Message):
    """
    Structure of request: handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
    The handshake must be 49+len(pstr) bytes long, pstr is 19 bytes long in BitTorrent v1
    So, overall length is 49+19 which gives us 68 overall length of the HandShake message
    """
    def __init__(self, info_hash, peer_id):
        super(HandShake, self).__init__()

        self.peer_id = peer_id
        self.info_hash = info_hash

        assert len(self.info_hash) == 20
        assert len(self.peer_id) < 255

    def to_bytes(self):
        # 8 reserved bytes
        reserved = b'\x00' * 8
        handshake = pack(">B{}s8s20s20s".format(LEN_HANDSHAKE_PSTR), LEN_HANDSHAKE_PSTR, HANDSHAKE_PSTR, reserved,
                         self.info_hash, self.peer_id)

        return handshake

    @classmethod
    def from_bytes(cls, payload):
        pstrlen, = unpack(">B", payload[:1])
        pstr, reserved, info_hash, peer_id = unpack("{}s8s20s20s".format(pstrlen), payload[1:])

        if pstrlen != LEN_HANDSHAKE_PSTR:
            raise ValueError

        return HandShake(info_hash, peer_id)


class KeepAlive(Message):
    """The structure of request: """
    def __init__(self):
        super(KeepAlive, self).__init__()
