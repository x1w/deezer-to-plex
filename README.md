# deezer-to-plex
Convert Deezer playlists to Plex playlists using existing songs on your Plex library

Simple script, delete the cache .json file if you've added any new songs to your Plex library, only stores to cache because scraping every song takes awhile for big libraries.

Good if you want to actually download songs:
https://github.com/m8tec/Deezync

Usage: 
python main.py

Ensure you set (at the top of main.py) file:
base_url
plex_token
