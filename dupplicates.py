import os
from os import walk

playlists = []
dupplicates = []
problems = []
nb_dupplicates = 0
print ("")
w = walk("C:/Temp/Playlists")
for (dirpath, dirnames, filenames) in w:
    for filename in filenames:
        if filename.endswith(".m3u"):
            with open(os.path.join(dirpath, filename)) as file:
                try:
                    playlist = os.path.basename(file.readline().rstrip('\n'))
                    if playlist is not None and playlist != '':
                        if playlist not in playlists:
                            playlists.append(playlist)
                        else:
                            nb_dupplicates += 1
                            print(f'Dupplicate {nb_dupplicates}: {playlist}')
                            dupplicates.append(playlist)
                except:
                    problems.append(os.path.join(dirpath, filename))
                    pass 
print ("")
for problem in problems:
    print(f"Issue with {problem}")
print ("")
print ("-- Analysis is complete ! --")
