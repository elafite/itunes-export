from pathlib import Path
from libpytunes import Library
from libpytunes import Playlist
import os
from os import walk
from subprocess import call
import shutil
import plistlib
import secrets
import speedcopy

STEP_1 = False
STEP_2 = True
STEP_3 = False
SANITY_CHECK = False

iTunesMusicRootPath = "P:/iTunes"
#iTunesLibrary = "P:/Musique/Bibliothèque.xml"
iTunesLibrary = "F:/Bibliothèque.xml"

root_folder = "F:"
iTunesRootFolder = root_folder + "/iTunes"
musicRootPath = root_folder + "/Music"
playlistRootPath = root_folder + "/Playlists2"
cleaniTunesLibrary = iTunesRootFolder + "/library2.xml"

if(not Path(iTunesRootFolder).exists()):
    Path(iTunesRootFolder).mkdir()
if(not Path(musicRootPath).exists()):
    Path(musicRootPath).mkdir()
if(not Path(playlistRootPath).exists()):
    Path(playlistRootPath).mkdir()

musicErrorFile = "Musique non répertoriée.txt"
playlistErrorFile = "Liens de playlists erronés.txt"

ignoreList = []
exportGeniusPlaylists = False
exportSmartPlaylists = False

iTunesMusicSubFolders = ["iTunes", "iTunes Media", "Music", "iTunes Music", "Albums MP3", "Amazon MP3", "MP"]
ignoreFolders = ["Ajouter automatiquement à iTunes", "Album Artwork", "Downloads", "iPod Games", "Mobile Applications",
                 "Podcasts", "Previous iTunes Libraries", ".thumbnails", "AcerCloud", "Playlists"]
ignorePlaylists = ["Bibliothèque", "Musique", "Téléchargé", "Films", "Morceaux Internet"]
extensions = [".mp3", ".m4a", ".wma"]

os.chdir (root_folder)

copy_errors = 0

def copy_clean(source: Path, destination: Path, lut : dict):
    global copy_errors
    #print (f"Traitement du répertoire: {source}")
    files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
    for file in files:
        file_path_source = source.joinpath(file)
        if file_path_source.suffix in extensions:
            file_path_dest = destination.joinpath(file)
            lut[file_path_source] = file_path_dest
            if STEP_1:
                if file_path_dest.is_file () is False:
                    #print (f"  copie de \"{file_path_source}\" vers \"{file_path_dest}\"")
                    try:
                        shutil.copy2 (file_path_source, file_path_dest)
                        #speedcopy.copyfile(file_path_source, file_path_dest)
                    except:
                        print (f"  /!\\ Erreur pendant la copie de {file_path_source} vers {file_path_dest}")

    folders = [d for d in os.listdir(source) if os.path.isdir(os.path.join(source, d))]
    for folder in folders:
        if folder not in ignoreFolders:
            if folder not in iTunesMusicSubFolders:
                copy_path = destination.joinpath(folder)
                if STEP_1:
                    if(not copy_path.exists()):
                        copy_path.mkdir()
                copy_clean (source.joinpath(folder), copy_path, lut)
            else:
                copy_clean (source.joinpath(folder), Path(musicRootPath), lut)


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
        # if(not currentPath.exists()):
        #     currentPath.mkdir()
        for childPlaylist in playlists.values():
            if(childPlaylist.parent_persistent_id == playlist.playlist_persistent_id):
                exportPlaylist(childPlaylist, currentPath)
    elif playlist.name not in ignorePlaylists:
        playlistContent = []
        content = []
        dupplicates = []
        for track in playlist.tracks:
            if track.location != None:
                fixed_track_location = Path(track.location)
                if fixed_track_location in musicLookUpTable:
                    playListsLookUpTable[musicLookUpTable[fixed_track_location]] = parentPath.joinpath(playlist.name + ".m3u")
                    new_track_location = os.path.relpath(musicLookUpTable[fixed_track_location], start=parentPath)
                    if new_track_location not in content:
                        content.append(new_track_location)
                        playlistContent.append(new_track_location)
                    # else:
                    #     print ("Dupplicate playlist content: " + str(new_track_location))
                    #     dupplicates.append(new_track_location)
                else:
                    #pln = cleanupPlaylistName(playlist.name) + ".m3u"
                    pln = os.path.relpath(parentPath.joinpath(playlist.name + ".m3u"),playlistRootPath)
                    if pln not in playlistErrors:
                        playlistErrors[pln] = []
                    playlistErrors[pln].append(fixed_track_location)

        playlistPath = parentPath.joinpath(cleanupPlaylistName(playlist.name) + ".m3u")
        if len (playlistContent) > 0:
            if(not parentPath.exists()):
                parentPath.makedirs(exist_ok=True)
            with open(playlistPath, "w", encoding='utf-8') as f:
                for link in playlistContent:
                    f.write(str(link) + "\n")

#####################################################################
#          Copy the music files in a clean structure                #
#####################################################################

print(f"\nEtape 1/3 - Copie des fichiers musicaux depuis {iTunesMusicRootPath} vers {musicRootPath}")

musicLookUpTable = {}
copy_clean (Path(iTunesMusicRootPath), Path(musicRootPath), musicLookUpTable)

if STEP_1:
    with open("LUT.txt", "w", encoding='utf-8') as f:
        for key, value in musicLookUpTable.items():
            f.write(f"{key} => {value}\n")

    print (f"  => table de correspondance sauvegardée dans {os.path.abspath("LUT.txt")}\n")
else:
    print("...skipped")
#####################################################################
#       Generate the M3U playlists + folder structure               #
#####################################################################
if STEP_2:
    print(f"Etape 2/3 - Exportation des playlists au format .m3u vers {playlistRootPath}")
    playlists = {}
    library = Library(iTunesLibrary)
    playListsLookUpTable = {}
    playlistErrors = {}
    for playlistID in library.getPlaylistIDs(ignoreList=[
            "Library", "Music", "Movies", "TV Shows", "Purchased", "iTunes DJ", "Podcasts", "Audiobooks", "Downloaded"
    ] + ignoreList):
        playlist = library.getPlaylistByID(playlistID)
        playlists[playlist.playlist_persistent_id] = playlist

    for playlist in playlists.values(): 
        if(playlist.parent_persistent_id == None) :
            exportPlaylist(playlist, Path(playlistRootPath))

    if len(playlistErrors.keys()) > 0:
        with open(playlistErrorFile, "w", encoding='utf-8') as f:
            f.write("************************************************************************\n")
            f.write("*  Fichiers musicaux non localisés lors de l'exportation des playlists *\n")
            f.write("************************************************************************\n")
            for playListName, links in playlistErrors.items():
                f.write(f"\nPlaylist {playListName}:\n")
                for link in links:
                    f.write (f"  - {link}\n")

        print (f"  => erreurs lors de l'exportation : voir {os.path.abspath(playlistErrorFile)}\n")
#####################################################################
#           Generate the clean iTunes library                       #
#####################################################################
if STEP_3:
    print(f"Etape 3/3 - Génération de la bibilothèque iTunes {cleaniTunesLibrary}")
    relativeRootSourceMusic = musicRootPath.split(':',1)[1]

    itemID = 1
    def generate_hex_string():
        return secrets.token_hex(8).upper()

    pl = {}

    pl['Music Folder'] = "file://localhost/" + musicRootPath
    pl['Library Persistent ID'] = generate_hex_string()

    ###### Generate the tracks list ##########
    tracks = {}

    for root, dirs, files in os.walk(musicRootPath):
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
        full_path = "file://localhost/" + musicRootPath + parts[1]
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

if STEP_3:
    walk_folder (playlistRootPath)

    if playlists:
        pl['Playlists'] = playlists
    ##########################################

    with open(cleaniTunesLibrary, "w", encoding='utf-8') as f:
        f.write(plistlib.dumps(pl, sort_keys=False).decode())

###############################################
#           Sanity check                      #
###############################################
if SANITY_CHECK:
    nb_orpheans = 0
    orpheans_music = {}

    for root, dirs, files in os.walk(musicRootPath):
        for name in files:
                filename = Path(os.path.join(root, name))
                if filename not in playListsLookUpTable.keys() and filename is not None:
                    nb_orpheans += 1
                    folder = Path (root)
                    if folder not in orpheans_music:
                        orpheans_music[folder] = []
                    orpheans_music[folder].append(name)

    # for root, dirs, files in os.walk(iTunesMusicRootPath):
    #    for name in files:
    #         filename = Path(os.path.join(root, name))
    #         if filename not in LookUpTable.keys() and filename is not None and filename.suffix in extensions:
    #             nb_orpheans += 1
    #             folder = Path (root)
    #             if folder not in orpheans_music:
    #                 orpheans_music[folder] = []
    #             orpheans_music[folder].append(name)

    if len(orpheans_music.keys()) > 0:
        with open(musicErrorFile, "w", encoding='utf-8') as f:
            f.write ("************************************************************\n")
            f.write ("*   Fichiers de musique non répertoriés dans les playlists *\n")
            f.write ("************************************************************\n")
            for root, files in orpheans_music.items():
                f.write (f"\n  Dans {root}:\n")
                for filename in files:
                    nb_orpheans += 1
                    f.write (f"    - {filename}\n")

            f.write(f"\n => Total: {nb_orpheans} fichiers non répertoriés")

        
        print (f"\nVérification: des fichiers musicaux ne sont pas répertoriés, voir {os.path.abspath(musicErrorFile)}\n")

print("\n-------- Exportation terminée --------\n")
