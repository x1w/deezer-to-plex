import requests
from plexapi.server import PlexServer
from rapidfuzz import fuzz
from plexapi.audio import Track
import json
import os
import re

base_url = "" # Plex base url, e.g: http://localhost:32400/
plex_token = "" # Plex auth token, https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
cache_file = "plex_tracks.json"
plex = PlexServer(base_url, plex_token)
playlists = [] # Playlists IDs to sync (list of strings) ensure playlists are public

print(f"Connected to Plex server: {plex.friendlyName}")

def get_deezer_playlist(id: str) -> list:
    url = f"https://api.deezer.com/playlist/{id}"
    tracks = []

    try:
        # Fetch playlist metadata
        response = requests.get(url, timeout=10)
        metadata = response.json()

        # Fetch tracks with pagnation
        url = f"https://api.deezer.com/playlist/{id}/tracks"
        while url:
            response = requests.get(url, timeout=10)
            data = response.json()
            tracks.extend(data.get('data', []))
            url = data.get('next', None)

        tracks.extend(data.get('data', []))
    except requests.RequestException as e:
        print(f"Failed to fetch Deezer playlist {id}")

    return {
        'name': metadata.get('title', ''),
        'picture': metadata.get('picture', ''),
        'tracks': tracks
    }

# Use cache file if exists
plex_tracks = []
if os.path.exists(cache_file):
    with open(cache_file, 'r') as f:
        plex_tracks = json.load(f)

# Find and store Plex tracks
if not plex_tracks:
    print("Storing Plex tracks to file")

    # Store Plex tracks
    music_library = plex.library.section('Music')
    for album in music_library.searchAlbums():
        for track in album.tracks():
            track: Track
            plex_tracks.append({
                'title': track.title,
                'artist':  track.grandparentTitle,
                'album':  track.parentTitle,
                'duration':  track.duration,
                'ratingKey': track.ratingKey
            })

    with open(cache_file, 'w') as f:
        json.dump(plex_tracks, f)

def clean_title(title: str) -> str:
    # Remove any form of (feat. ...), [ft ...], (featuring ...), etc.
    return re.sub(r'\s*[\(\[]?(feat|featuring|ft)\.? [^\)\]]+[\)\]]?', '', title, flags=re.IGNORECASE).strip().lower()

# Matches pretty close, made it more lenient
def match_track(deezer_track):
    d_title = clean_title(deezer_track['title'])
    d_artist = deezer_track['artist']['name'].lower()
    d_duration = deezer_track['duration']
    d_isrc = deezer_track['isrc'] # dunno if plex has

    for track in plex_tracks:
        track: Track
        p_title = clean_title(track['title'])
        p_artist = track['artist'].lower().lower()
        
        p_duration = int(track['duration'] / 1000)

        title_score = fuzz.token_set_ratio(d_title, p_title)
        artist_score = fuzz.token_set_ratio(d_artist, p_artist)
        duration_score = abs(d_duration - p_duration) <= 4
        title_similarity = fuzz.token_set_ratio(d_title, p_title) / 100

        # adjust to your liking
        if (title_score > 80 and artist_score > 70) or \
        (title_score > 80 and duration_score) or \
        (title_score > 60 and artist_score > 65 and duration_score) or \
        (title_similarity >= 0.99):
            return track

    print(f"no match: {d_title}")

for id in playlists:
    playlist = get_deezer_playlist(id)

    if not playlist:
        continue

    print(f"playlist: {playlist["name"]}")
    found = []
    for track in playlist['tracks']:
        p_track = match_track(track)
        if not p_track: 
            continue

        found.append(plex.fetchItem(p_track['ratingKey']))

    print(f"playlist: {playlist['name']}, found {len(found)}/{len(playlist['tracks'])} track matches")

    # Add playlist to Plex
    plex_playlist = plex.createPlaylist(playlist['name'], items=found)
