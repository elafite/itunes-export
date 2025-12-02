from libpytunes import Library
from libpytunes import Playlist
from pathlib import Path
import os

#iTunesLibrary = "P:/Musique/Bibliothèque.xml"
iTunesLibrary = "F:/Bibliothèque.xml"
playlistRootPath = Path("F:/PlaylistsNew")
musicFolder = "F:/Music"
#iTunesMediaFolders = ["F:/Musique/iTunes/iTunes Media/iTunes Media/iTunes Music", "F:/Musique/iTunes/iTunes Media/Music", "F:/Musique/iTunes/iTunes Media", "F:/Musique/iTunes/iTunes Music", "F:/Musique/iTunes"]
iTunesMediaFolders = ["F:/Music/iTunes/iTunes Media/iTunes Media/iTunes Music", "F:/Musique/iTunes/iTunes Media/Music", "F:/Musique/iTunes/iTunes Media", "F:/Musique/iTunes/iTunes Music", "F:/Musique/iTunes"]
ignoreList = []
exportGeniusPlaylists = False
exportSmartPlaylists = False

def fix_track_location(path):
       for s in iTunesMediaFolders:
        if path.startswith(s):
                return path.replace(s, musicFolder)
       print("Path not found: " + path)
       return path

def cleanupPlaylistName(playlistName):
        return playlistName.replace("/", "").replace("\\", "").replace(":", "_").replace("\"", "_").replace("?", "_")

def exportPlaylist(playlist: Playlist, parentPath: Path):
        if(playlist.is_genius_playlist and not exportGeniusPlaylists):
                return

        if(playlist.is_smart_playlist and not exportSmartPlaylists):
                return
        
        if(playlist.is_folder):
                # Create Folder
                currentPath = parentPath.joinpath(cleanupPlaylistName(playlist.name))
                if(not currentPath.exists()):
                        currentPath.mkdir()
                for childPlaylist in playlists.values():
                        if(childPlaylist.parent_persistent_id == playlist.playlist_persistent_id):
                                exportPlaylist(childPlaylist, currentPath)
        else:
                playlistContent = ""
                content = []
                dupplicates = []
                for track in playlist.tracks:
                        if track.location != None:
                                fixed_track_location = fix_track_location (track.location)
                                if fixed_track_location not in content:
                                       content.append(fixed_track_location)
                                else:
                                       print ("Dupplicate playlist content: " + fixed_track_location)
                                       dupplicates.append(fixed_track_location)
                                try:
                                        playlistContent +=  os.path.relpath(fixed_track_location, start=parentPath) + "\n"
                                except ValueError:
                                        print("Warning: Could not add the track \"" + track.location + "\" as relative path to the playlist \"" + playlist.name + "\"; added the track as absolute path instead.")
                                        playlistContent += track.location + "\n"

                playlistPath = parentPath.joinpath(cleanupPlaylistName(playlist.name) + ".m3u")
                if len (playlistContent) > 0:
                        if(not parentPath.exists()):
                                os.makedirs(parentPath, exist_ok=True)
                        playlistPath.write_text(playlistContent, encoding="utf8")


playlists = {}

library = Library(iTunesLibrary)

for playlistID in library.getPlaylistIDs(ignoreList=[
        "Library", "Music", "Movies", "TV Shows", "Purchased", "iTunes DJ", "Podcasts", "Audiobooks", "Downloaded"
] + ignoreList):
    playlist = library.getPlaylistByID(playlistID)
    playlists[playlist.playlist_persistent_id] = playlist

for playlist in playlists.values(): 
    if(playlist.parent_persistent_id == None) :
        exportPlaylist(playlist, playlistRootPath)