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
prompt = config["prompt"]
prompt_var = f"{prompt}"
test_image_output_folder = "test_image_output/"

def sd_api_call(dirpath, artist_item, title_item):
    global api_call_count
    global test_folder_enabled
    global stable_diffusion_address
    global prompt_var
    global print_artist_item
    global print_track_item
    global blur_level

    # Increment the total api call counter
    api_call_count += 1

    if dry_run_enabled:
        return

    # api call to local stable diffusion instance
    url = f"{stable_diffusion_address}"

    print(f"prompt: {prompt_var}")
    payload = {
        "prompt": f"{prompt_var}",
        "negative_prompt": "((text)), ((humans)), ((faces)), bodies, disconnected arms, disconnected legs, deformed face, ugly face, disappearing thigh, malformed, couch, sofa, pillow, living room, cheap, low budget, low quality, poor",
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
        font_size = 40
        font = ImageFont.load_default()

        # Set position of artist text
        outline_color = 'black'
        text_color = 'white'
        text = f"{artist_item}"
        # If artist_item is too large, size down the font to fit the image
        img_fraction = 0.95
        while font_size > 9:
            font = ImageFont.load_default()
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
        font_size = 40
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
        image.save(f'{dirpath}\\cover.png', pnginfo=metadata)
        print(f"image successfully created, tagged, and moved to {dirpath}\\cover.png. sleeping for {sleep_timer}s\n")

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

    # check if there is any artwork attached to the file ("artwork" tag)
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

    # check if cover.png exists (common artwork format)
    if os.path.isfile(f"{dirpath}\\cover.png") and bool(regenerate_ai_artwork):
        print("cover art exists (cover.png). checking if ai generated")
        if check_author_ai(f"{dirpath}\\cover.png"):
            print("cover.png detected to be ai generated. regenerating")
            sd_api_call()
        else:
            print("cover.png detected to be ai generated, but regenerate_ai_artwork is set to false. Skipping\n")

    # check if AlbumArt.jpg exists (common artwork format)
    elif os.path.isfile(f"{dirpath}\\AlbumArt.jpg"):
        print("cover art exists (AlbumArt.jpg). skipping this file\n")

    else:
        print("cover art does not exist. calling stable diffusion api")
        print(f"sending sd api call:\ntitle: {tag['title']}\nartist: {tag['artist']}")
        sd_api_call(dirpath, tag["artist"], tag['title'])
        print(f"Total images created: {api_call_count}")
        print("changing directory\n")
        

def main():
    args = argument_parser()

    start_time = time.time()

    if not os.path.exists(test_image_output_folder):
        os.makedirs(test_image_output_folder)

    # Walk through the directory and scan files for file types (.mp3, .opus, etc)
    for dirpath, dirs, files in os.walk(music_directory):
        print(f"Current Directory: {dirpath}")
        print(f"Found Files: {files}")
        for musicfile in files:
            if musicfile.endswith(".mp3"):
                check_and_generate(dirpath, musicfile, music_extension=".mp3")
            elif musicfile.endswith(".opus"):
                check_and_generate(dirpath, musicfile, music_extension=".opus")
            elif musicfile.endswith((".jpg", ".png")):
                print(f"potential cover art found: {musicfile}.")
            else:
                print(f"unsupported file type: {dirpath}/{musicfile}/n")

    print("Scipt complete in %s seconds" % (time.time() - start_time))
    print(f"Total images created: {api_call_count}")

def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument("--music_directory", type=str, help="Full directory path for your music directory. example: /mnt/data/Music, or C:\\Users\\user\\Music")
    parser.add_argument("--icon_path", type=str, help="Path to icon. If you use a custom icon, it should be size 150x150. Currently, only .png files supported")
    parser.add_argument("--sleep_timer", type=int, help="The number of seconds the script will sleep after each image created. Helps with GPU temperatures, but slows the process down")
    parser.add_argument("--dry_run_enabled", type=bool, help="Skip generating new images, instead will just analyze the music_directory and print results in the console")
    parser.add_argument("--regenerate_ai_artwork", type=bool, help="Every cover.png in the music_directory or subdirectories that has the 'Author' tag set to 'AI' will be deleted and regenerated")
    parser.add_argument("--blur_level", type=int, help="0 = No blur effect applied, 5 = high blur. Blur can make SD images appear less ugly at a glance")
    parser.add_argument("--stable_diffusion_address", type=str, help="Use API calls to public or paid instances at your own risk")
    
    parser.add_argument("--prompt", type=str)
    parser.add_argument("--test_image_output_folder", type=str)

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
