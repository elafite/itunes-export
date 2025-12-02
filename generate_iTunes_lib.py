import datetime
import plistlib
import secrets
import os
from pathlib import Path

rootSourceMusic = "F:/Music2" 
relativeRootSourceMusic = rootSourceMusic.split(':',1)[1]
rootSourcePlaylists = "F:/Playlists2"
iTunesLibrary = "F:/iTunes/library2.xml"

itemID = 1
def generate_hex_string():
    return secrets.token_hex(8).upper()

pl = {}

pl['Music Folder'] = "file://localhost/" + rootSourceMusic
pl['Library Persistent ID'] = generate_hex_string()

###### Generate the tracks list ##########
tracks = {}

for root, dirs, files in os.walk(rootSourceMusic):
   for name in files:
        track = {}
        track['Track ID'] = itemID
        track['Persistent ID'] = generate_hex_string()
        track['Track Type'] = "File"
        track['Location'] = "file://localhost/" + os.path.join(root, name).replace("\\", "/")
        tracks[str(itemID)] = track
        itemID += 1

pl['Tracks'] = tracks
##########################################

def get_track_id (file_path):
    parts = file_path.replace("\\", "/").replace("\n","").split(relativeRootSourceMusic, 1)  # Split at "/Music" once
    if len(parts) > 1:
        full_path = "file://localhost/" + rootSourceMusic + parts[1]
        for trackId, track in tracks.items():
            if track['Location'] == full_path:
                return int(trackId)
    else:
        return None
###### Generate the playlists ##########
playlists = []

def walk_folder(path: Path, parent_persistent_id = None):
    global itemID
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    for file in files:
        playlist = {}
        playlist['Name'] = str(Path(file).with_suffix(''))
        playlist['Playlist ID'] = itemID
        playlist['Playlist Persistent ID'] = generate_hex_string()
        if parent_persistent_id is not None:
            playlist['Parent Persistent ID'] = parent_persistent_id
        playlist['All Items'] = True
        playlist_items = []
        with open(os.path.join(path, file), encoding='utf-8') as playlist_file:
            for file_path in playlist_file:
                #file_path = playlist_file.readline()
                trackID = get_track_id (file_path)
                if trackID is not None:
                    a_track = {}
                    a_track['Track ID'] = trackID
                    playlist_items.append (a_track)
        if playlist_items:
            playlist['Playlist Items'] = playlist_items
            playlists.append(playlist)
            itemID += 1
    folders = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    for folder in folders:
        playlist = {}
        playlist['Name'] = folder
        playlist['Playlist ID'] = itemID
        playlist['Playlist Persistent ID'] = generate_hex_string()
        if parent_persistent_id is not None:
            playlist['Parent Persistent ID'] = parent_persistent_id
        playlist['All Items'] = True
        playlist['Folder'] = True
        playlists.append(playlist)
        itemID += 1
        walk_folder (os.path.join(path, folder), playlist['Playlist Persistent ID'])

walk_folder (rootSourcePlaylists)

if playlists:
    pl['Playlists'] = playlists
##########################################

with open(iTunesLibrary, "w", encoding='utf-8') as f:
    f.write(plistlib.dumps(pl, sort_keys=False).decode())

print("Librairie générée avec succès")
