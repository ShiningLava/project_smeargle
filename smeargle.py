# This script will check if artwork exists for music files in the music_directory,
# and if not it will call upon a local stable diffusion API to generate it.
# If regenerate_ai_artwork is set to true, this script will regenerate any cover.png that it detects to have "AI" as the author tag.
# This script will need read and write access to the music_directory and subdirectories.
# This script will need read access to the icon_path.

import json
import os
import music_tag
import io
import base64
import random
import requests
import time
import json
from PIL.PngImagePlugin import PngInfo
from PIL import Image, PngImagePlugin, ImageFilter, ImageFont, ImageDraw

import argparse

VERSION = "1.1.0"

with open('config.json', 'r') as g:
    config = json.load(g)

start_time = time.time()
api_call_count = 0
unsupported_file_count = 0
music_directory = config['music_directory']
icon_path = config['icon_path']
sleep_timer = config['sleep_timer']
dry_run_enabled = config['dry_run_enabled']
test_folder_enabled = config['test_folder_enabled']
stable_diffusion_address = config['stable_diffusion_address']
regenerate_ai_artwork = config['regenerate_ai_artwork']
print_artist_item = config['print_artist_item']
print_track_item = config['print_track_item']
print_icon = config['print_icon']
blur_level = config['blur_level']
prompt = config['prompt']
prompt_var = f"{prompt}"
test_image_output_folder = "test_image_output/"
negative_prompt = config['negative_prompt']
negative_prompt_var = f"{negative_prompt}"
sd_progress = 0
unsupported_file_list = []

def sd_api_call(dirpath, artist_item, title_item):
    global api_call_count
    global test_folder_enabled
    global stable_diffusion_address
    global prompt_var
    global print_artist_item
    global print_track_item
    global blur_level
    global sd_progress

    # arg parser stuff (need to consolidate)
    args = argument_parser()
    dry_run_enabled = args.dry_run_enabled
    icon_path = args.icon_path

    # below errors out and/or needs fixes to default values
    #blur_level = args.blur_level
    #sleep_timer = args.sleep_timer
    #stable_diffusion_address = args.stable_diffusion_address
    #prompt_var = f"{args.prompt}"
    #print_artist_item = args.print_artist_item
    #print_icon = args.print_icon

    # console says that it saves cover.png in test folder but it doesn't really
    #test_folder_enabled = args.test_folder_enabled

    # below errors out due to previous errors (font found on windows but not linux)
    #print_track_item = args.print_track_item



    sd_progress = 0

    # Increment the total api call counter
    api_call_count += 1

    if dry_run_enabled:
    	sd_progress += 1
    	return

    # api call to local stable diffusion instance
    url = f"{stable_diffusion_address}"

    print(f"prompt: {prompt_var}")
    payload = {
        "prompt": f"{prompt_var}",
        "negative_prompt": f"{negative_prompt_var}",
        "width": 400,
        "height": 400,
        "steps": 25
    }

    response = requests.post(url=f'{url}', json=payload)

    r = response.json()

    # encode the api's response into base64 and process into .png, save to directory
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}', json=png_payload)
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save('output2.png', pnginfo=pnginfo)

    # blur the SD image
    im = Image.open("output2.png")
    im1 = im.filter(ImageFilter.BoxBlur(blur_level))
    im1.save('im1.png', pnginfo=pnginfo)

    # Watermark
    if bool(print_icon) == True:
        original_image = Image.open('im1.png')
        watermark = Image.open(icon_path)
        transparency = 135
        watermark = watermark.convert('RGBA')
        watermark_with_transparency = Image.new('RGBA', watermark.size)
        for x in range(watermark.width):
            for y in range(watermark.height):
                r, g, b, a = watermark.getpixel((x, y))
                if not (r == 0 and g == 0 and b == 0):
                    watermark_with_transparency.putpixel((x, y), (r, g, b, transparency))
        position = (269, 251)
        original_image.paste(watermark_with_transparency, position, watermark_with_transparency)

        # Draw the watermark on the image
        original_image.save('im1.png')

    # impose text over SD image
    # Load an image
    image = Image.open('im1.png')
    draw = ImageDraw.Draw(image)

    if bool(print_artist_item) == True:
        # Set font properties for artist text
        font_size = 100
        font = ImageFont.load_default(font_size)

        # Set position of artist text
        outline_color = 'black'
        text_color = 'white'
        text = f"{artist_item}"
        # If artist_item is too large, size down the font to fit the image
        img_fraction = 0.95
        while font_size > 9:
            font = ImageFont.load_default(font_size)
            if font.getlength(text) < img_fraction * 400:
                break
            else:
                font_size -= 1
        text_width = font.getlength(text)
        text_height = font_size
        if font.getlength(text) < img_fraction * 400:
            x = (im1.width - text_width) // 2
        else:
            x = (im1.width - text_width) // 50
        y = ((im1.height - text_height) // 2) + 125

        # Draw the artist text on the image
        draw.text((x, y), text, fill=text_color, font=font, stroke_width=2, stroke_fill=outline_color)

        # Save image
        image.save('im1.png')

    if bool(print_track_item) == True:
        # Set font properties for artist text
        font_size = 100
        font = ImageFont.truetype('times', font_size)

        # Set position of track_item
        outline_color = 'black'
        text_color = 'white'
        text = f"{title_item}"
        img_fraction = 0.95
        while font_size > 9:
            font = ImageFont.truetype("ariblk.ttf", font_size)
            if font.getlength(text) < img_fraction * 400:
                break
            else:
                font_size -= 1
        text_width = font.getlength(text)
        text_height = font_size
        if font.getlength(text) < img_fraction * 400:
            x = (im1.width - text_width) // 2
        else:
            x = (im1.width - text_width) // 50
        y = ((im1.height - text_height) // 2) + 75

        #text_height = font_size
        #text_width = draw.textlength(text, font)
        #x = (im1.width - text_width) // 2
        #y = ((im1.height - text_height) // 2) + 10

        # Draw the track text on the image
        draw.text((x, y), text, fill=text_color, font=font, stroke_width=2, stroke_fill=outline_color)

        # Save image
        image.save('im1.png')

    # Add "Author = AI" tag
    image = Image.open('im1.png')
    metadata = PngInfo()
    metadata.add_text('Author', 'AI')
    if bool(test_folder_enabled) == True:
        image.save(f'test_image_output/{api_call_count}.png', pnginfo=metadata)
        print(f"image successfully created, tagged, and moved to test_image_output/{api_call_count}.png. sleeping for {sleep_timer}s")
    else:
        image.save(f'{dirpath}/cover.png', pnginfo=metadata)
        print(f"image successfully created, tagged, and moved to {dirpath}/cover.png. sleeping for {sleep_timer}s\n")

    sd_progress += 1

    # Sleep (helps break up GPU tasks for better temperatures)
    time.sleep(sleep_timer)


def check_author_ai(dirpath, name:str = "AI"):
    im = Image.open(dirpath)
    im.load()
    return im.info['Author'] == name

def check_and_generate(dirpath, musicfile, music_extension):
    musicfilepath = os.path.join(dirpath, musicfile)
    print(f"{music_extension} found: {musicfilepath}")
    tag = music_tag.load_file(f"{musicfilepath}")
    args = argument_parser()

    # arg parser stuff (consolidate this later)
    regenerate_ai_artwork = args.regenerate_ai_artwork


    # check if there is any artwork attached to the file ("artwork" tag)
    # can likely consolidate a lot of this logic as .opus so far is the only file type that needs extra logic
    if music_extension == ".mp3":
        	try:
        		if bool(tag['artwork'].first):
        			print("non ai-generated art found. skipping file (.mp3)\n")
        			return
        	except:
        		print("keyError .mp3\n")

    elif music_extension == ".opus":
        	try:
        		if bool(tag['artwork'].first):
        			print("non ai-generated art found. skipping file (.opus)\n")
        			return
        	except:
        		print(".opus found with no attached artwork. checking if cover.png exists")

    elif music_extension == ".flac":
    	try:
    		if bool(tag['artwork'].first):
    			print("non ai-generated art found. skipping file (.flac)\n")
    			return
    	except:
    		print(".flac found with no attached artwork. checking if cover.png exists\n")
    #elif music_extension == ".aac":
    	#print("AAC FOUND BUT SUPPORT IS NOT YET ADDED\n")
    	#return
    elif music_extension == ".wav":
        try:
                if bool(tag['artwork'].first):
                        print("non ai-generated art found. skipping file (.wav)\n")
                        return
        except:
                print(".wav found with no attached artwork. checking if cover.png exists\n")
    #elif music_extension == ".mkv":
        #print("MKV FOUND BUT SUPPORT IS NOT YET ADDED\n")
        #return

    elif music_extension == ".m4a":
        try:
                if bool(tag['artwork'].first):
                        print("non ai-generated art found. skipping file (.m4a)\n")
                        return
        except:
                print(".m4a found with no attached artwork. checking if cover.png exists\n")

    # check if cover.png exists (common artwork format)
    if os.path.isfile(f"{dirpath}/cover.png"):
        print("cover art exists (cover.png). checking if ai generated")
        if check_author_ai(f"{dirpath}/cover.png") and bool(regenerate_ai_artwork):
            print("cover.png detected to be ai generated. regenerating")
            sd_api_call(dirpath, tag["artist"], tag['title'])
            print(f"Total images created: {api_call_count}\n")
        else:
            print("cover.png detected to be ai generated, but regenerate_ai_artwork is set to false. Skipping\n")

    # check if AlbumArt.jpg exists (common artwork format)
    elif os.path.isfile(f"{dirpath}/AlbumArt.jpg"):
        print("cover art exists (AlbumArt.jpg). skipping this file\n")

    else:
        print("cover art does not exist. calling stable diffusion api")
        print(f"sending sd api call:\ntitle: {tag['title']}\nartist: {tag['artist']}")
        sd_api_call(dirpath, tag['artist'], tag['title'])
        print(f"Total images created: {api_call_count}\n")

def main():
    args = argument_parser()

    # below is disabled due to default values not working properly
    #music_directory = args.music_directory
    
    global unsupported_file_count
    global unsupported_file_list

    start_time = time.time()

    if not os.path.exists(test_image_output_folder):
        os.makedirs(test_image_output_folder)

    # Walk through the directory and scan files for file types (.mp3, .opus, etc)
    # After image creation, break to change directories to prevent duplicate work
    for dirpath, dirs, files in os.walk(music_directory):
        print(f"Current Directory: {dirpath}")
        print(f"Found Files: {files}")
        for musicfile in files:
            musicfilepath = os.path.join(dirpath, musicfile)
            if musicfile.endswith(".mp3"):
                check_and_generate(dirpath, musicfile, music_extension=".mp3")
                if sd_progress > 0:
                	break
            elif musicfile.endswith(".opus"):
                check_and_generate(dirpath, musicfile, music_extension=".opus")
                if sd_progress > 0:
                	break
            elif musicfile.endswith(".flac"):
                check_and_generate(dirpath, musicfile, music_extension=".flac")
                if sd_progress > 0:
                	break
            #elif musicfile.endswith(".aac"):
            	#check_and_generate(dirpath, musicfile, music_extension=".aac")
            elif musicfile.endswith(".wav"):
                check_and_generate(dirpath, musicfile, music_extension=".wav")
            #elif musicfile.endswith(".mkv"):
                #check_and_generate(dirpath, musicfile, music_extension=".mkv")
            elif musicfile.endswith(".m4a"):
                check_and_generate(dirpath, musicfile, music_extension=".m4a")
            elif musicfile.endswith((".jpg", ".png")):
                print(f"potential cover art found: {musicfile}")
            else:
                print(f"unsupported file type: {dirpath}/{musicfile}\n")
                unsupported_file_count += 1
                unsupported_file_list += [musicfilepath]

    print("Scipt complete in %s seconds" % (time.time() - start_time))
    print(f"Total images created: {api_call_count}")
    if unsupported_file_count > 0:
    	print(f"Total files skipped due to unsupported file types: {unsupported_file_count}")
    	print(f"Unsupported files: {unsupported_file_list}")

def argument_parser():
    parser = argparse.ArgumentParser()

    # lines disabled below are not currently functioning and need work (most likely due to defaults)
    parser.add_argument("--config", type=argparse.FileType('r', encoding='UTF-8'))
    #parser.add_argument("--music_directory", type=str, help="Full directory path for your music directory. example: /mnt/data/Music, or C:\\Users\\user\\Music")
    parser.add_argument("--icon_path", type=str, help="Path to icon. If you use a custom icon, it should be size 150x150. Currently, only .png files supported")
    #parser.add_argument("--sleep_timer", type=int, help="The number of seconds the script will sleep after each image created. Helps with GPU temperatures, but slows the process down")
    parser.add_argument("--dry_run_enabled", type=bool, help="Skip generating new images, instead will just analyze the music_directory and print results in the console")
    parser.add_argument("--regenerate_ai_artwork", type=bool, help="Every cover.png in the music_directory or subdirectories that has the 'Author' tag set to 'AI' will be deleted and regenerated")
    #parser.add_argument("--blur_level", type=int, help="0 = No blur effect applied, 5 = high blur. Blur can make SD images appear less ugly at a glance")
    #parser.add_argument("--stable_diffusion_address", type=str, help="Use API calls to public or paid instances at your own risk")
    #parser.add_argument("--prompt", type=str)
    #parser.add_argument("--test_image_output_folder", type=str)

    # This could take a string, and if set use that path otherwise do the default
    parser.add_argument("--test_folder_enabled", type=bool, help="Save each stable diffusion image to /project_smeargle/test_image_output/ rather than placing the image with the music file")

    # Maybe add help for these?
    parser.add_argument("--print_artist_item", type=bool)
    parser.add_argument("--print_track_item", type=bool)
    parser.add_argument("--print_icon", type=bool)

    # If we get a json config file, it will set the defaults
    args, unknown = parser.parse_known_args()

    if args.config:
        try:
            config = json.load(args.config)
            parser.set_defaults(**config)
        except Exception as e:
            print(e)

    return parser.parse_args()

if __name__ == "__main__":
    main()
