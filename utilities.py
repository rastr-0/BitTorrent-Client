import logging
from torrent import Torrent

LOG = logging.getLogger('')
INFO_HASH = None
PEER_ID = None
HANDSHAKE_PSTR = b"BitTorrent protocol"
LEN_HANDSHAKE_PSTR = len(HANDSHAKE_PSTR)