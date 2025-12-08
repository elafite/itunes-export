import xml.etree.ElementTree as ET
import os
from urllib.parse import unquote, urlparse
from pathlib import Path

# Configuration
iTunesSourceLibrary = "F:/iTunes/iTunes Library (original).xml"
iTunesFixedLibrary = "F:/iTunes/iTunes Library (clean).xml"
iTunesMusicSubFolders = ["iTunes", "iTunes Media", "Music", "iTunes Music", 
                         "Albums MP3", "Amazon MP3", "MP"]
iTunesSourceRootPath = "P:/Musique/iTunes"
iTunesDestRootPath = "C:/Users/berna/Music/iTunes/Music"
iTunesCheckPath = "F:/Music"
MusicReferencePath = "P:/iTunes"

def fix_music_path(original_path):
    """
    Fix the music path by:
    1. Replacing the source root with destination root
    2. Removing any subfolder from iTunesMusicSubFolders that appears after the root
    """
    # Handle file:// URLs
    if original_path.startswith('file://'):
        # Parse and decode the URL
        parsed = urlparse(original_path)
        decoded_path = unquote(parsed.path)
        # Remove leading slash on Windows paths
        if decoded_path.startswith('/') and ':' in decoded_path:
            decoded_path = decoded_path[1:]
    else:
        decoded_path = original_path
    
    # Normalize path separators
    decoded_path = decoded_path.replace('/', os.sep).replace('\\', os.sep)
    source_root = iTunesSourceRootPath.replace('/', os.sep).replace('\\', os.sep)
    
    # Check if path starts with source root
    if not decoded_path.startswith(source_root):
        return original_path  # Return unchanged if not matching
    
    # Get the relative path after the source root
    relative_path = decoded_path[len(source_root):].lstrip(os.sep)
    
    # Split the relative path into parts
    parts = relative_path.split(os.sep)
    
    # Remove any parts that match iTunesMusicSubFolders
    filtered_parts = [p for p in parts if p not in iTunesMusicSubFolders]
    
    # Reconstruct the path with destination root
    new_relative = os.sep.join(filtered_parts)
    new_path = os.path.join(iTunesDestRootPath, new_relative)
    
    # Convert back to file:// URL format if original was a URL
    if original_path.startswith('file://'):
        new_path = 'file://localhost/' + new_path.replace(os.sep, '/')
    
    return new_path

def process_itunes_library():
    """
    Read iTunes library XML, fix paths, and write to new file
    """
    print(f"Reading: {iTunesSourceLibrary}")
    
    # Parse the XML file
    tree = ET.parse(iTunesSourceLibrary)
    root = tree.getroot()
    
    # iTunes library format: root > dict > ...
    # Find all track entries and fix their locations
    main_dict = root.find('dict')
    if main_dict is None:
        print("Error: Could not find main dictionary in iTunes library")
        return
    
    tracks_found = False
    current_key = None
    paths_fixed = 0
    paths_not_found = []
    
    # Iterate through dict children
    for elem in main_dict:
        if elem.tag == 'key':
            current_key = elem.text
        elif elem.tag == 'dict' and current_key == 'Tracks':
            tracks_found = True
            # Process each track
            for track_elem in elem:
                if track_elem.tag == 'dict':
                    # Process track dictionary
                    track_name = None
                    for i, child in enumerate(track_elem):
                        if child.tag == 'key' and child.text == 'Name':
                            if i + 1 < len(track_elem):
                                name_elem = track_elem[i + 1]
                                if name_elem.tag == 'string':
                                    track_name = name_elem.text
                        elif child.tag == 'key' and child.text == 'Location':
                            # Next element should be the location string
                            if i + 1 < len(track_elem):
                                location_elem = track_elem[i + 1]
                                if location_elem.tag == 'string':
                                    old_path = location_elem.text
                                    new_path = fix_music_path(old_path)
                                    if old_path != new_path:
                                        location_elem.text = new_path
                                        paths_fixed += 1
                                        
                                        # Check if the new file path exists
                                        check_path = new_path
                                        if check_path.startswith('file://localhost/'):
                                            check_path = check_path[17:]
                                            # parsed = urlparse(check_path)
                                            # check_path = unquote(parsed.path)
                                            # if check_path.startswith('/') and ':' in check_path:
                                            #     check_path = check_path[1:]
                                        fake_path = check_path.replace(iTunesDestRootPath, iTunesCheckPath)
                                        
                                        if not os.path.exists(fake_path):
                                            paths_not_found.append({
                                                'track': track_name or 'Unknown',
                                                'path': check_path
                                            })
    
    if not tracks_found:
        print("Warning: No tracks dictionary found in library")
    else:
        print(f"Fixed {paths_fixed} music paths")
        
        # Report missing files
        if paths_not_found:
            print(f"\nWarning: {len(paths_not_found)} file(s) not found:")
            for item in paths_not_found[:20]:  # Show first 20
                print(f"  - {item['track']}")
                print(f"    {item['path']}")
            if len(paths_not_found) > 20:
                print(f"  ... and {len(paths_not_found) - 20} more")
            
            # Save missing files report
            report_file = iTunesFixedLibrary.replace('.xml', '_missing_files.txt')
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"Missing Files Report - {len(paths_not_found)} files not found\n")
                f.write("=" * 80 + "\n\n")
                for item in paths_not_found:
                    f.write(f"Track: {item['track']}\n")
                    f.write(f"Path:  {item['path']}\n\n")
            print(f"\nFull report saved to: {report_file}")
        else:
            print("\nAll files found successfully!")
    
    # Write the modified XML to new file
    print(f"\nWriting: {iTunesFixedLibrary}")
    tree.write(iTunesFixedLibrary, encoding='utf-8', xml_declaration=True)
    print("Done!")

if __name__ == "__main__":
    # Check if source file exists
    if not os.path.exists(iTunesSourceLibrary):
        print(f"Error: Source library not found: {iTunesSourceLibrary}")
    else:
        process_itunes_library()