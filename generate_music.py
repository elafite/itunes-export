from pathlib import Path
import os
from os import walk
import shutil

iTunesMusicRootPath = "I:/Musique"
root_folder = "F:"
iTunesRootFolder = root_folder + "/iTunes"
musicRootPath = root_folder + "/Music"

iTunesMusicSubFolders = ["iTunes", "iTunes Media", "Music", "iTunes Music", "Albums MP3", "Amazon MP3", "MP"]
ignoreFolders = ["Ajouter automatiquement à iTunes", "Album Artwork", "Downloads", "iPod Games", "Mobile Applications",
                 "Podcasts", "Previous iTunes Libraries", ".thumbnails", "AcerCloud", "Playlists", ]
extensions = [".mp3", ".m4a", ".wma"]

def copy_clean(source: Path, destination: Path, lut : dict):
    print (f"Traitement du répertoire: {source}")
    files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
    for file in files:
        file_path_source = source.joinpath(file)
        if file_path_source.suffix in extensions:
            file_path_dest = destination.joinpath(file)
            lut[file_path_source] = file_path_dest
            if file_path_dest.is_file () is False:
                #print (f"  copie de \"{file_path_source}\" vers \"{file_path_dest}\"")
                shutil.copy2 (file_path_source, file_path_dest)

    folders = [d for d in os.listdir(source) if os.path.isdir(os.path.join(source, d))]
    for folder in folders:
        if folder not in ignoreFolders:
            if folder not in iTunesMusicSubFolders:
                copy_path = destination.joinpath(folder)
                if(not copy_path.exists()):
                    #print (f"Make dir {copy_path}")
                    copy_path.mkdir()
                copy_clean (source.joinpath(folder), copy_path, lut)
            else:
                copy_clean (source.joinpath(folder), Path(musicRootPath), lut)

print ("")

LookUpTable = {}
copy_clean (Path(iTunesMusicRootPath), Path(musicRootPath), LookUpTable)

print ("")
print ("-- Export terminé --")
