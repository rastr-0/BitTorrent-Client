from utilities import HANDSHAKE_PSTR, LEN_HANDSHAKE_PSTR
from struct import pack, unpack


class NotImplementedMessageError(Exception):
    pass


class WrongMessageType(Exception):
    pass


class WrongMessageException(Exception):
    pass


class MessageDispatcher:
    """Message dispatcher class which determines
        the type of message based on the payload"""
    def __init__(self, payload_param):
        self.payload = payload_param

    def dispatch(self):
        message_id = -1
        try:
            if len(self.payload) >= 5:
                payload_length, message_id, = unpack(">IB", self.payload[:5])
        except Exception:
            raise NotImplementedMessageError("Error occur while unpacking buffer")

        messages_ids = {
            0: Choke,
            1: Unchoke,
            2: Interested,
            3: NotInterested,
            4: Have,
            5: None,  # Bitfield
            6: None,  # Request
            7: None,  # Piece
            8: None,  # Cancel
            9: None,  # Port
        }

        if message_id not in messages_ids:
            raise WrongMessageType(f"Message with following id: {message_id} doesn't exist")

        return messages_ids[message_id].from_bytes(self.payload)


class Message:
    """Base class"""
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
    """The structure of request:
        <len=0000>(4 bytes)"""
    payload_length = 0
    total_length = 4

    def __init__(self):
        super(KeepAlive, self).__init__()

    def to_bytes(self):
        return pack(">I", self.payload_length)

    @classmethod
    def from_bytes(cls, payload):
        payload_length = unpack(">I", payload[:cls.total_length])

        if payload_length != 0:
            raise WrongMessageType("Not a KeepAlive message")

        return KeepAlive()


class Choke(Message):
    """The structure of request:
        <len=0001>(4 bytes)<id=0>(1 byte)"""
    message_id = 0

    payload_length = 1
    total_length = 5

    def __init__(self):
        super(Choke, self).__init__()

    def to_bytes(self):
        return pack(">IB", self.payload_length, self.message_id)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, message_id = unpack(">IB", payload[:cls.total_length])
        if message_id != cls.message_id:
            raise WrongMessageType("Not a Choke message")

        return Choke()


class Unchoke(Message):
    """The structure of request:
        <len=0001>(4 bytes)<id=1>(1 byte)"""
    message_id = 1

    payload_length = 1
    total_length = 5

    def __init__(self):
        super(Unchoke, self).__init__()

    def to_bytes(self):
        return pack(">IB", self.payload_length, self.message_id)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, message_id = unpack(">IB", payload[:cls.total_length])
        if message_id != cls.message_id:
            raise WrongMessageType("Not an Unchoke message")

        return Unchoke()


class Interested(Message):
    """The structure of request:
        interested: <len=0001>(4 bytes)<id=2>(1 byte)"""
    message_id = 2

    payload_length = 1
    total_length = 5

    def __init__(self):
        super(Interested, self).__init__()

    def to_bytes(self):
        return pack(">IB", self.payload_length, self.message_id)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, message_id = unpack(">IB", payload[:cls.total_length])
        if message_id != cls.message_id:
            raise WrongMessageType("Not an Interested message")

        return Interested()


class NotInterested(Message):
    """The structure of request:
        interested: <len=0001>(4 bytes)<id=3>(1 byte)"""
    message_id = 3

    payload_length = 1
    total_length = 5

    def __init__(self):
        super(NotInterested, self).__init__()

    def to_bytes(self):
        return pack(">IB", self.payload_length, self.message_id)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, message_id = unpack(">IB", payload[:cls.total_length])
        if message_id != cls.message_id:
            raise WrongMessageType("Not an Interested message")

        return NotInterested()


class Have(Message):
    """The structure of request:
        <len=0005>(4 bytes)<id=4>(1 byte)<piece index>"(4 bytes)"""
    message_id = 4

    payload_length = 5
    total_length = 9

    def __init__(self, piece_index):
        super(Have, self).__init__()
        self.piece_index = piece_index

    def to_bytes(self):
        return pack(">IBI", self.payload_length, self.message_id, self.piece_index)

    @classmethod
    def from_bytes(cls, payload):
        payload_length, message_id, piece_index = unpack(">IBI", payload[:cls.total_length])
        if message_id != cls.message_id:
            raise WrongMessageType("Not a Have message")

        return Have(piece_index)


class BitField(Message):
    """The structure of request:
        <len=0001+X>(4 bytes)<id=5>(1 byte)<bitfield>(x bytes)"""
    message_id = 5

    def __init__(self, bitfield):
        super(BitField, self).__init__()
        self.bitfield = bitfield
        self.bitfield_bytes = self.bitfield.to_bytes()
        self.bitfield_length = len(self.bitfield_bytes)

        self.payload_length = 1 + self.bitfield_length
        self.total_length = 4 + self.payload_length

    def to_bytes(self):
        return pack(">IB{}s".format(self.bitfield_length),
                    self.payload_length,
                    self.message_id,
                    self.bitfield_bytes)

    @classmethod
    def from_bytes(cls, payload):
        from bitstring import BitArray

        payload_length, message_id = unpack(">IB", payload[:5])
        bitfield_length = payload_length - 1

        if message_id != cls.message_id:
            raise WrongMessageType("Not a BitField message")

        raw_bitfield = unpack(">{}s".format(bitfield_length), payload[5:5 + bitfield_length])
        bitfield_bytes = BitArray(bytes=bytes(raw_bitfield))

        return BitField(bitfield_bytes)
