class BitTorrentError(Exception):
    pass


class TrackerError(BitTorrentError):
    pass


class PeerConnectionError(BitTorrentError):
    pass


class PieceVerificationError(BitTorrentError):
    pass
