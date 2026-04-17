import argparse
import logging

from bittorrent.domain.torrent_meta import TorrentMeta
from bittorrent.network.tracker import HTTPTracker
from bittorrent.orchestration.torrent_session import TorrentSession


def main():
    parser = argparse.ArgumentParser(description="BitTorrent client")
    parser.add_argument("torrent_file", help="Path to the .torrent file")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    meta = TorrentMeta()
    meta.load_file(args.torrent_file)

    tracker = HTTPTracker(
        announce_url=meta.announce_list[0][0],
        info_hash=meta.info_hash,
        peer_id=meta.peer_id,
    )
    tracker.set_stats(left=meta.file_size)

    session = TorrentSession(meta, tracker, meta.get_filename())
    session.start()
    session.join()


if __name__ == "__main__":
    main()
