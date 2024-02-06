# Small BitTorrent client by rastr-0

## Description
This is bittorrent client implementation with Python.
Main features:
#### Torrent File Parsing:
  * The client has the ability to parse .torrent files, extracting essential information required for the download process
#### Tracker Communication:
  * The client can make requests to trackers, although currently limited to trackers that support HTTP responses. Implementation for UDP trackers is in progress
#### Bittorrent Message Logic
  * The client implements the core logic for handling various Bittorrent messages:
    * Choke/UnChoke messages: indicating whether the client is allowed to downloaded from the peer
    * Interested/NotInterested messages: indicating whether the peer is interested in downloading piece
    * Request messages: requests specific block of a piece from the peer
    * Piece messages: response to request message with data
    * Have and Bitfield messages: updating information about presented pieces for the peer
    * Classes for Port and Cancel messages are implemented, though the logic handling is not implemented yet
## Table of Contests

- [Installation](#installation)

## Installation
1. Clone the repository to your local system
   ```shell
   git clone https://github.com/rastr-0/BitTorrent-Client.git
2. Change your working directory to the project folder
   ```shell
   cd BitTorrent-Client
3. Install the requered dependencies
   ```shell
   pip install -r requirements.txt
4. Run main and pass your .torrent file
   ```shell
   python3 main.py
