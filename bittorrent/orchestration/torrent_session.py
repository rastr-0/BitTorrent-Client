import time
import logging
from threading import Thread

from bittorrent.domain import message
from bittorrent.domain.block import State
from bittorrent.domain.torrent_meta import TorrentMeta
from bittorrent.network.peer_manager import PeerManager
from bittorrent.orchestration.piece_manager import PieceManager
from bittorrent.storage.file_storage import FileStorage


class TorrentSession(Thread):
    def __init__(self, meta: TorrentMeta, tracker, output_path: str):
        super().__init__()
        self._meta = meta
        self._completed_blocks = 0
        self._completed_percentage = 0.0

        self._piece_manager = PieceManager(meta)
        self._storage = FileStorage(self._piece_manager, output_path)
        self._peer_manager = PeerManager(
            self._piece_manager,
            info_hash=meta.info_hash,
            number_of_pieces=meta.number_of_pieces,
        )

        peers = tracker.get_peers()
        self._peer_manager.connect_to_peers(peers)
        self._peer_manager.start()
        self._storage.start()

    def run(self):
        while not self._piece_manager.all_pieces_completed():
            if self._peer_manager.unchoked_peers_count() < 1:
                time.sleep(1.0)
                continue

            for piece in self._piece_manager.pieces:
                idx = piece.piece_index

                if self._piece_manager.pieces[idx].is_full:
                    continue

                peer = self._peer_manager.get_random_peer_with_piece(idx)
                if not peer:
                    continue

                block_data = self._piece_manager.pieces[idx].get_empty_block()
                if not block_data:
                    continue

                self._piece_manager.pieces[idx].update_block_status()

                piece_index, block_offset, block_length = block_data
                request = message.Request(piece_index, block_offset, block_length).to_bytes()

                if not peer.healthy:
                    self._peer_manager.disconnect_peer(peer)
                    continue

                peer.send_message(request)
                time.sleep(0.1)

                self._report_progress()

    def _report_progress(self):
        blocks_done = sum(
            sum(1 for b in piece.blocks if b.state == State.FULL)
            for piece in self._piece_manager.pieces
        )
        if blocks_done > 0 and blocks_done != self._completed_blocks:
            self._completed_blocks = blocks_done
            total_blocks = sum(len(p.blocks) for p in self._piece_manager.pieces)
            percentage = round(blocks_done / total_blocks * 100, 2)
            if percentage != self._completed_percentage:
                self._completed_percentage = percentage
                print(f"Downloaded {self._completed_percentage}%")
