# Small BitTorrent client by rastr-0

## Table of Contests
- [Overview](#overview)
- [Components](#components)
- [Installation](#installation)
- [Problems](#problems)
- [Resources](#resources)

## Overview
This is a bittorrent client implementation with Python. I want to emphasize that this is just a basic implementation made by layman in bittorrents and programming in general.
If you are planning to create your own implementation of BitTorrent, you are absolutely welcome to use mine for figuring out something. But keep in mind, it's not perfect in all senses 🙂

### Main features:
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
#### Saving process with using virtual memory:
  * Mmap library is used in saving process which makes saving process quite fast 

## Components:
Architecture for this project was not invetnted by me. It's, in fact, quite popular solution for BitTorrent clients.
Project is OOP based and contains 10 files:
  * main.py - __RunBittorrent__ class which, primary,  runs other classes in threads and have high-level logic for handling piece messages from peers
  * torrent.py - __Torrent__ class with functionality for opening, reading and parsing .torrent file; also has functionality for performing requests to tracker
  * utilities.py - auxiliary functions and constants, such as BLOCK_SIZE, INFO_HASH, HANDSHAKE_PSTR
  * block.py - __Block__ class for representing the part of piece and State class with possible states of block
  * piece.py - __Piece__ class represents one Piece and provides appropriate functionality, such as initializing blocks, updating blocks states, getting block states
  * piece_manager.py - __PieceManager__ class is implemented for initializing pieces and keeping track of their states, based on which are performed further operations
  * peer.py - __Peer__ class describes peer and provides functionality for handling all type of messages and buffer reading
  * peer_manager.py - __PeerManager__ class (thread derived) with functionality for doing operations which apply to all peers (connection, disconnection, message processing and calling specific handling function from Peer class)
  * message.py - has 1 base class __Message__ and derived classes for representing individual type of messages. The most important functions of each class are from_bytes(encoding) and to_bytes (decoding)
  * file_writer.py - __BlockSaver__ class (thread derived) has functionality for saving blocks with FULL state, mmap library is used for speeding saving process.
  
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

## Problems
As I wrote in an overview part my project is a basic implementation with plenty of work for the future. Main problems for now are:
  * Not implemented functionality to work with .torrent files that contain multi-files for downloading
  * Client doesn't verify downloaded pieces hashes with original pieces hashes (this one will be fixed soon).
  * They way pieces are downloaded. Blocks are requested not one by one in the same piece, but one by one from different pieces (first block from each piece; second block each piece...). There is following deriving problem from it:
    * Peer can't start participating as a seeder while downloading pieces, because peer will have 1 fully downloaded piece (n downloaded blocks) only after downloading (n-1 blocks for other pieces)
  * No ability to stop downloading process and continue with already downloaded pieces (not to start over)

## Resources
This project wouldn't exist without these resources and projects:
  * https://wiki.theory.org/BitTorrentSpecification (Bittorrent Protocol Specification)
  * https://roadmap.sh/guides/torrent-client (Implementation with JS, author explains everything in simple words)
  * https://github.com/gallexis/PyTorrent (Absolutely great implementation of BitTorrent from @gallexis, my messages classes are 100% based on this project messages classes)
  * https://github.com/SimplyAhmazing (Also useful stuff, @SimpleAhmazing also has lecture on YouTube about Bittorrent implementation with python)
