# deezer-to-plex
Convert Deezer playlists to Plex playlists using existing songs on your Plex library

Simple script, delete the cache .json file if you've added any new songs to your Plex library, only stores to cache because scraping every song takes awhile for big libraries.

If you want to actually download songs:
https://github.com/m8tec/Deezync

### Configuration
`base_url` Your Plex server's URL  <br> 
`plex_token` Plex authentication token [(steps to obtain)]([https://github.com/nathom/streamrip/wiki/Finding-Your-Deezer-ARL-Cookie](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)) <br> 
`playlists` List of public Deezer playlist IDs e.g: ["11118352144", "2021225582"] <br> 

### Usage
`pip install -r requirements.txt`<br> 
`python main.py`

