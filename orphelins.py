from libpytunes import Library
from libpytunes import Playlist
from pathlib import Path
import pathlib
import os
import argparse

libraryPath = "F:/Music/iTunes Library.xml"
rootSource = "J:/Music"

songs = []
extensions = []

def exportPlaylist(playlist: Playlist):
        if(playlist.is_folder):
            for childPlaylist in playlists.values():
                if(childPlaylist.parent_persistent_id == playlist.playlist_persistent_id):
                    exportPlaylist(childPlaylist)
        else:
            for track in playlist.tracks:
                if track.location != None:
                    song = os.path.basename(track.location)
                    if song not in songs:
                            songs.append(song)
                    extension = pathlib.Path(track.location).suffix
                    if extension not in extensions:
                         extensions.append(extension)

playlists = {}

library = Library(libraryPath)
for playlistName in library.getPlaylistNames(ignoreList=[
        "Library", "Music", "Movies", "TV Shows", "Purchased", "iTunes DJ", "Podcasts", "Audiobooks", "Downloaded"
]):
    playlist = library.getPlaylist(playlistName)
    playlists[playlist.playlist_persistent_id] = playlist

for playlist in playlists.values(): 
    if(playlist.parent_persistent_id == None) :
        exportPlaylist(playlist)

print (f"Il y a {len(songs)} pistes dans la playlist")

orpheans = []

for root, dirs, files in os.walk(rootSource):
   for name in files:
        extension = pathlib.Path(name).suffix
        if extension in extensions and name not in songs:
            if name in orpheans:
                  print("Piste en double: " + name)
            else:
                orpheans.append(os.path.join(root, name))
print (f"Il y a {len(orpheans)} pistes non référencées dans les listes de lecture")
for name in orpheans:
     print (f"Piste non référencée: {name}")

