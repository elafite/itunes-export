import os
from os import walk
import shutil


# rootSource = "I:/Musique/iTunes/iTunes Media"
# rootSource = "I:/Musique/iTunes/iTunes Media/Music"
rootSource = "I:/Musique/iTunes/iTunes Music"
rootDest = "J:/Music"

ignoreFolders = ["Ajouter automatiquement à iTunes", "Album Artwork", "Downloads", "iPod Games", "Music", "Podcasts", "Previous iTunes Libraries", "Unknown Artist (2)"]
print ("")

folders = [d for d in os.listdir(rootSource) if os.path.isdir(os.path.join(rootSource, d))]

for folder in folders:
    copy_folder = os.path.join(rootDest, folder)
    if os.path.isdir(copy_folder) is False and folder not in ignoreFolders:
        print ("Copying " + folder + "...")
        shutil.copytree(os.path.join(rootSource, folder), copy_folder)

print ("")
print ("-- Analysis is complete ! --")
