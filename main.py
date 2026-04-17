from bittorrent.domain.torrent_meta import TorrentMeta
from bittorrent.network.tracker import HTTPTracker
from bittorrent.orchestration.torrent_session import TorrentSession

if __name__ == '__main__':
    print("Your .torrent file: ")
    torrent_file = str(input())

    meta = TorrentMeta()
    meta.load_file(torrent_file)

    tracker = HTTPTracker(
        announce_url=meta.announce_list[0][0],
        info_hash=meta.info_hash,
        peer_id=meta.peer_id,
    )
    tracker.set_stats(left=meta.file_size)

    session = TorrentSession(meta, tracker, meta.get_filename())
    session.start()
    session.join()
