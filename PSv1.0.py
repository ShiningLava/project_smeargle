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
# "prompt" : "dark, high contrast, cosmic setting, beautiful, intense dark blue and cyan galaxies, planets, stars, high quality, high detail",

def sd_api_call():
    global api_call_count
    global test_folder_enabled
    global stable_diffusion_address
    global prompt_var
    global print_artist_item
    global print_track_item
    global blur_level

    # Increment the total api call counter
    api_call_count += 1

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
        font = ImageFont.truetype("ariblk.ttf", font_size)

        # Set position of artist text
        outline_color = 'black'
        text_color = 'white'
        text = f"{artist_item}"
        # If artist_item is too large, size down the font to fit the image
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
        image.save(f'{dirpath}\cover.png', pnginfo=metadata)
        print(f"image successfully created, tagged, and moved to {dirpath}\cover.png. sleeping for {sleep_timer}s\n")

    # Sleep (helps break up GPU tasks for better temperatures)
    time.sleep(sleep_timer)

if not os.path.exists(test_image_output_folder):
    os.makedirs(test_image_output_folder)

# Walk through the directory and scan files for file types (.mp3, .opus, etc)
for dirpath, dirs, files in os.walk(music_directory):
    print(f"Current Directory: {dirpath}")
    print(f"Found Files: {files}")
    for musicfile in files:
        if musicfile.endswith(".mp3"):
            musicfilepath = os.path.join(dirpath, musicfile)
            print(f".mp3 found: {musicfilepath}")
            f = music_tag.load_file(f"{musicfilepath}")
            title_item = f['title']
            artist_item = f['artist']
            art = f['artwork']
            comment_item = f['comment']
            # check if there is any artwork attached to the .mp3 file ("artwork" tag)
            if bool(art.first) == True:
                print("non ai-generated art found. skipping file\n")
            # check if AlbumArt.jpg exists (common artwork format)
            elif os.path.isfile(f"{dirpath}\AlbumArt.jpg"):
                print("cover art exists (AlbumArt.jpg). skipping\n")
            # check if cover.png exists (common artwork format)
            elif os.path.isfile(f"{dirpath}\cover.png"):
                print("cover art exists (cover.png). checking if ai generated")
                im = Image.open(f'{dirpath}\cover.png')
                im.load()
                if im.info['Author'] == str("AI"):
                    if bool(regenerate_ai_artwork) == True:
                        print("cover.png detected to be ai generated. regenerating")
                        if bool(dry_run_enabled) == False:
                            sd_api_call()
                        elif bool(dry_run_enabled) == True:
                            api_call_count += 1
                        break
                    elif bool(regenerate_ai_artwork) == False:
                        print("cover.png detected to be ai generated, but regenerate_ai_artwork is set to false. Skipping\n")
                        break
            else:
                print("cover art does not exist. calling stable diffusion api")
                print(f"sending sd api call:\ntitle: {title_item}\nartist: {artist_item}")
                if bool(dry_run_enabled) == False:
                    sd_api_call()
                elif bool(dry_run_enabled) == True:
                    api_call_count += 1
                print(f"Total images created: {api_call_count}")
                print("changing directory\n")
                break
        elif musicfile.endswith(".opus"):
            musicfilepath = os.path.join(dirpath, musicfile)
            print(f".opus found: {musicfilepath}")
            print(f"directory: {dirpath}")
            f = music_tag.load_file(f"{musicfilepath}")
            title_item = f['title']
            artist_item = f['artist']
            # check if cover.png exists (common artwork format)
            if os.path.isfile(f"{dirpath}\cover.png"):
                print("cover art exists (cover.png). checking if ai generated")
                im = Image.open(f'{dirpath}\cover.png')
                im.load()
                # check if cover.png's author is "AI" (signature of images generated by this script)
                if im.info['Author'] == str("AI"):
                    if bool(regenerate_ai_artwork) == True:
                        print("cover.png detected to be ai generated. regenerating")
                        if bool(dry_run_enabled) == False:
                            sd_api_call()
                        elif bool(dry_run_enabled) == True:
                            api_call_count += 1
                        break
                    elif bool(regenerate_ai_artwork) == False:
                        print("cover.png detected to be ai generated, but regenerate_ai_artwork is set to false. Skipping\n")
                        break
            # check if AlbumArt.jpg exists (common artwork format)
            elif os.path.isfile(f"{dirpath}\AlbumArt.jpg"):
                print("cover art exists (AlbumArt.jpg). skipping this file\n")
                break
            else:
                print("cover art does not exist. calling stable diffusion api")
                print(f"sending sd api call:\ntitle: {title_item}\nartist: {artist_item}")
                if bool(dry_run_enabled) == False:
                    sd_api_call()
                elif bool(dry_run_enabled) == True:
                    api_call_count += 1
                print(f"Total images created: {api_call_count}")
                print("changing directory\n")
                break
        elif musicfile.endswith(".jpg" or ".png"):
            print(f"potential cover art found: {musicfile}.")
        else:
            print(f"unsupported file type: {dirpath}/{musicfile}")
            print("changing directory\n")

print("Scipt complete in %s seconds" % (time.time() - start_time))
print(f"Total images created: {api_call_count}")