# This script will target any cover.png files made by Project Smeargle for deletion.
# Currently, this is any cover.png in the music_directory which
# has the author tag set to 'AI' (signature of Project Smeargle).
# This script requires read and write access to cover.png files in the music_directory and subdirectories.

import os
import music_tag
import time
import json
from PIL import Image

start_time = time.time()
image_delete_count = 0

with open('config.json', 'r') as g:
    config = json.load(g)

music_directory = config['music_directory']
dry_run_enabled = config['dry_run_enabled']

def check_author_ai(dirpath, name:str = "AI"):
    im = Image.open(dirpath)
    im.load()
    return im.info['Author'] == name

# Walk the directory and search for cover.png that has 'author' tag as 'AI'
for dirpath, dirs, files in os.walk(music_directory):
        print(f"Current Directory: {dirpath}")
        print(f"Found Files: {files}\n")
        for musicfile in files:
            if musicfile.endswith(("cover.png")):
                print(f"cover art found: {musicfile}. checking if ai generated")
                if check_author_ai(f"{dirpath}/cover.png") == True:
                	print("cover.png found to be ai generated. deleting image")
                	if bool(dry_run_enabled):
                		image_delete_count += 1
                		print(f"dry_run_enabled, image not deleted. {image_delete_count}\n")
                		break
                	else:
                		os.remove(f"{dirpath}/cover.png")
                		image_delete_count += 1
                		print(f"image deleted. {image_delete_count}\n")
                else:
                	print("non ai generated image found. skipping")

print(f"Scipt complete in %s seconds" % (time.time() - start_time))
print(f"Total images deleted: {image_delete_count}")
