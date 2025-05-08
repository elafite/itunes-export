import os

root_folder = "F:"
music_path = "F:/Music"
playlists_path = "F:/Playlists"

invalid_links = {}
orpheans_music = {}
songs = []
playlists = {}
nb_music_files = 0
nb_playlists = 0

os.chdir (root_folder)

def get_playlist_links (filename):
    pl_refs = []
    for pl, s in playlists.items():
        if filename in s:
           pl_refs.append(pl) 
    return pl_refs

for root, dirs, files in os.walk(playlists_path):
   for name in files:
        with open(os.path.join(root, name), encoding='utf-8') as playlist_file:
            nb_playlists += 1
            pl_file = playlist_file.name.replace("\\","/")
            playlists[pl_file] = []
            for music_link in playlist_file:
                if music_link is not None:
                    filename = os.path.abspath (music_link).replace("\\","/").replace("\n","")
                    playlists[pl_file].append(filename)

for root, dirs, files in os.walk(music_path):
   for name in files:
        filename = os.path.join(root, name).replace("\\","/")
        if filename not in songs and filename is not None:
            nb_music_files += 1
            songs.append(filename)
            pl_refs = get_playlist_links (filename)
            if not pl_refs:
                folder = root.replace("\\","/")
                if not folder in orpheans_music:
                    orpheans_music[folder] = []
                orpheans_music[folder].append(name)

for pl, s in playlists.items():
    for filename in s:
        if filename not in songs:
            if not pl in invalid_links:
                invalid_links[pl] = []
            invalid_links[pl].append(filename)

print (f"Nombre total de fichiers musicaux: {nb_music_files}")
print (f"Nombre total de fichiers playlists: {nb_playlists}")

lines = []

nb_orpheans = 0
lines.append ("******************************************\n")
lines.append ("*   Fichiers de musique non répertoriés  *\n")
lines.append ("******************************************\n")
for root, files in orpheans_music.items():
    lines.append (f"\n  Dans {root}:\n")
    for filename in files:
        nb_orpheans += 1
        lines.append (f"    - {filename}\n")

lines.append(f"\n => Total: {nb_orpheans} fichiers non répertoriés\n\n")

with open("Musique non répertoriée.txt", "w", encoding='utf-8') as f:
    f.writelines (lines)

print (f"Fichier {os.path.abspath("Musique non répertoriée.txt")} généré")

lines = []

nb_invalid_links = 0
lines.append ("******************************************\n")
lines.append ("*      Liens de playlist non valides     *\n")
lines.append ("******************************************\n")

for pl, s in invalid_links.items():
    lines.append (f"\n  Dans {pl}:\n")
    for filename in s:
        nb_invalid_links += 1
        lines.append (f"    - {filename}\n")

lines.append(f"\n => Total: {nb_invalid_links} liens de playlist non valides")

with open("Liens de playlist invalides.txt", "w", encoding='utf-8') as f:
    f.writelines (lines)

print (f"Fichier {os.path.abspath("Liens de playlist invalides.txt")} généré")

print (f"Analyse terminée.")