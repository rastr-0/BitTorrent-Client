from typing import Protocol

import requests
from bcoding import bdecode

from bittorrent.exceptions import TrackerError


class TrackerProtocol(Protocol):
    """Interface for tracker communication."""
    def get_peers(self) -> list[dict]: ...


class HTTPTracker:
    """Synchronous HTTP tracker client."""

    def __init__(self, announce_url: str, info_hash: bytes, peer_id: bytes,
                 port: int = 6881):
        self._announce_url = announce_url
        self._info_hash = info_hash
        self._peer_id = peer_id
        self._port = port
        self._uploaded = 0
        self._downloaded = 0
        self._left = 0
        self._event = 'started'

    def set_stats(self, left: int, downloaded: int = 0, uploaded: int = 0) -> None:
        self._left = left
        self._downloaded = downloaded
        self._uploaded = uploaded

    def get_peers(self) -> list[dict]:
        params = {
            "info_hash": self._info_hash,
            "peer_id": self._peer_id,
            "port": self._port,
            "uploaded": self._uploaded,
            "downloaded": self._downloaded,
            "left": self._left,
            "event": self._event,
        }
        try:
            response = requests.get(self._announce_url, params=params, verify=False)
        except requests.RequestException as exc:
            raise TrackerError(f"Tracker request failed: {self._announce_url}") from exc
        if not response:
            raise TrackerError(f"Empty response from tracker: {self._announce_url}")
        return bdecode(response.text)['peers']
