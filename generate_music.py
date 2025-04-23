from pathlib import Path
import os
from os import walk
import shutil


destination = Path("F:/Music")
ignoreFolders = ["Ajouter automatiquement à iTunes", "Album Artwork", "Downloads", "iPod Games", "iTunes Media", "iTunes Music", "Mobile Applications", "Podcasts", "Previous iTunes Libraries", "Unknown Artist (2)", ".thumbnails", "Music"]
extensions = [".mp3", ".m4a"]

def copy_clean(source: Path, destination: Path):
    files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
    for file in files:
        file_path_source = source.joinpath(file)
        if file_path_source.suffix in extensions:
            file_path_dest = destination.joinpath(file)
            if file_path_dest.is_file () is False:
                shutil.copy2 (file_path_source, file_path_dest)

    folders = [d for d in os.listdir(source) if os.path.isdir(os.path.join(source, d))]
    for folder in folders:
        if folder not in ignoreFolders:
            copy_path = destination.joinpath(folder)
            if(not copy_path.exists()):
                copy_path.mkdir()
            copy_clean (source.joinpath(folder), copy_path)

print ("")

copy_clean (Path("I:/Musique/iTunes"), destination)
copy_clean (Path("I:/Musique/iTunes/iTunes Media"), destination)
copy_clean (Path("I:/Musique/iTunes/iTunes Media/Music"), destination)
copy_clean (Path("I:/Musique/iTunes/iTunes Music"), destination)

print ("")
print ("-- Export is complete ! --")
