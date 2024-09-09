# project_smeargle
Thanks for checking out Project Smeargle!


Current version: v1.0

Last revision date: Sep 08 2024

Music players tested: Plex, Plexamp, VLC

Currently supported music file types: .mp3, .opus


Project Smeargle is a few python scripts that are designed to detect if your music files are missing artwork. If they are, PS will send an API call to a locally hosted Stable Diffusion instance to generate some artwork. After image generation, the image will (optionally) be processed to include the artist, song title, as well as a logo printed on the image. This processed image will then be saved as a cover.png file alongside the music file, with image tags and a watermark to indicate that it is AI generated. 


Once the image is saved and the process is finished, many music players will be able to detect the new album artwork and can display it when playing the music. 



Setup Guide:
- download + setup stable diffusion + api
	- https://github.com/AUTOMATIC1111/stable-diffusion-webui
   
- Linux:
	- git clone https://github.com/ShiningLava/project_smeargle.git
	- apt install python3-venv
	- cd project_smeargle
	- python3 -m venv venv
	- source venv/bin/activate
	- pip install -r requirements.txt
	- nano config.json
		- change music_directory and stable_diffusion_url
	- python PSv1.0.py
	
- run the script, watch console for summary at the end
- play around with config.json and have fun


FAQ:

Q: Is this going to delete or ruin my current artwork? Or corrupt my music?
A: No. PS is designed to not write anything to your music files directly. PS will read your music files to check their artist, title, and artwork tags, however, PS should never delete or modify any existing data on the music files themselves. Instead, PS will generate a cover.png file for any music it determines to not have artwork. Always make sure you have a backup of important data before running unknown scripts from the internet.


Q: How do I set up Stable Diffusion? 
A: You'll need to see Stable Diffusion documentation for this. https://github.com/AUTOMATIC1111/stable-diffusion-webui


Q: How do I enable the Stable Diffusion API?
A: Once you have Stable Diffusion set up locally, you can edit the webui-user.bat file to include "--api" in the COMMANDLINE_ARGS. Once you reload the Stable Diffusion application, the API should be exposed. You can confirm the API is exposed by going to http://<stable_diffusion_ip>:7860/docs in a web browser. If Stable Diffusion is hosted on the same machine, you can go to the loopback address at http://127.0.0.1:7860/docs



Q: How do I get rid of the images made by this script?
A: Run the Cover_Image_Remover.py script. It's recommended to set dry_run_enabled = true in config.json file first to test the script. Once you are satisfied with the results printed in the console, set dry_run_enabled = false in config.json and run the script again to actually delete PS images.


Q: I ran PSv1.0.py but I didn't get any artwork with my music. What gives?
A: Check config.json file and double check dry_run_enabled and test_folder_enabled. Dry runs will skip generating art and will skip deleting art. Test folder which hosts images if test_folder_enabled = true, can be found at /project_smeargle/test_image_output/. 


Q: Why don't you support more file types?
A: PS should have support for more file types soon^(tm). I would like to add support for .wav, .flac, .aac, .mkv, and more


Q: Why the space theme for the Stable Diffusion prompt?
A: I'm not good at prompting in Stable Diffusion at the moment. Space is an easy theme for SD to make as it's easy to hide simple AI mistakes, as well as generally making images that aren't ugly to look at. If you feel like you can make better prompts, feel free to edit the "prompt" in config.json!


Q: Can I change the parameters of the API call?
A: Yes, however this must be done in the PSv1.0.py script instead of config.json. This can be found near the top of the custom defined function "sd_api_call()" in the script. If you would like to adjust these settings, please see the example in the Stable Diffusion txt2img API documentation at http://<stable_diffusion_ip>:7860/docs#/default/text2imgapi_sdapi_v1_txt2img_post for syntax guidance. 


Q: Your code sucks?
A: Yes. 


BEFORE AND AFTER:

![abstractum - miss u (before and after)](https://github.com/user-attachments/assets/7b7c5308-0279-4a41-803b-3710bcc0ac65)
![Satl   Malaky - Loneliness (before and after)](https://github.com/user-attachments/assets/b97132a4-105a-4e51-a35a-41a7706e343d)

