from libpytunes import Library
from libpytunes import Playlist
from pathlib import Path
import os
import argparse

parser = argparse.ArgumentParser(description="An utility application to export iTunes playlists in m3u format.")
parser.add_argument("--output_playlists", "-o", help="The outpout folder for exporting the playlists.", required=True)
parser.add_argument("--output_music", "-om", help="The outpout folder for exporting the music.")
parser.add_argument("--music_folder", "-m", help="The folder where the music files are stored", required=True)
parser.add_argument("--ignore", help="Ignore a specific playlist.", action='append')
parser.add_argument("--library", "-l", help="The path to the iTunes Library XML.", default=str(Path.home().joinpath("Music/iTunes/iTunes Music Library.xml")))
parser.add_argument("--export-genius-playlists", action='store_true', dest='exportGeniusPlaylists')
parser.add_argument("--export-smart-playlists", action='store_true', dest='exportSmartPlaylists')
parser.add_argument("--absolute", action='store_true', dest='absolute')
#parser.set_defaults(absolute=False)
args = parser.parse_args()

libraryPath = args.library
playlistRootPath = Path(args.output_playlists)
musicRootPath = Path(args.output_music) if args.output_music is not None else None
musicFolder = args.music_folder
ignoreList = args.ignore if args.ignore is not None else []

def fix_track_location(path):
       start = ["P:/Musique/iTunes/iTunes Media/Music", "P:/Musique/iTunes/iTunes Media", "P:/Musique/iTunes/iTunes Music", "P:/Musique/iTunes"]
       for s in start:
        if path.startswith(s):
                return path.replace(s, musicFolder)
       print("Path not found: " + path)
       return path

def cleanupPlaylistName(playlistName):
        return playlistName.replace("/", "").replace("\\", "").replace(":", "").replace("\"", "'").replace("?", "")

def exportPlaylist(playlist: Playlist, parentPath: Path):
        if(playlist.is_genius_playlist and not args.exportGeniusPlaylists):
                return

        if(playlist.is_smart_playlist and not args.exportSmartPlaylists):
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
                                #fixed_track_location = track.location.replace("P:/Musique/iTunes", musicFolder)
                                fixed_track_location = fix_track_location (track.location)
                                if fixed_track_location not in content:
                                       content.append(fixed_track_location)
                                else:
                                       print ("Dupplicate playlist content: " + fixed_track_location)
                                       dupplicates.append(fixed_track_location)
                                if args.absolute is True:
                                       playlistContent += fixed_track_location + "\n"
                                else:
                                        try:
                                                playlistContent +=  os.path.relpath(fixed_track_location, start=parentPath) + "\n"
                                        except ValueError:
                                                print("Warning: Could not add the track \"" + track.location + "\" as relative path to the playlist \"" + playlistName + "\"; added the track as absolute path instead.")
                                                playlistContent += track.location + "\n"

                playlistPath = parentPath.joinpath(cleanupPlaylistName(playlist.name) + ".m3u")
                playlistPath.write_text(playlistContent, encoding="utf8")

playlists = {}

library = Library(libraryPath)
for playlistName in library.getPlaylistNames(ignoreList=[
        "Library", "Music", "Movies", "TV Shows", "Purchased", "iTunes DJ", "Podcasts", "Audiobooks", "Downloaded"
] + ignoreList):
    playlist = library.getPlaylist(playlistName)
    playlists[playlist.playlist_persistent_id] = playlist

for playlist in playlists.values(): 
    if(playlist.parent_persistent_id == None) :
        exportPlaylist(playlist, playlistRootPath)