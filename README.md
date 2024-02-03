# Small BitTorrent client by rastr-0

## Description
This is bittorrent client implementation with Python.
Main features include:
  * Ability to parse .torrent files and make requests to tracker (only trackers that support HTTP responses, UDP are not implemented yet)
  * Implemented logic of bittorrent messages:
    * Choke/UnChoke messages
    * Interested/NotInterested messages
    * Request messages
    * Piece messages
    * Have and Bitfield messages
    * Classes for Port and Cancel messages are implemented, but there are no logic handling logic in code yet
