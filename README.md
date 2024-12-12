# project_smeargle
Thanks for checking out Project Smeargle!

Music players tested: Plex, Plexamp, VLC

### Currently supported music file types: .mp3, .opus, .flac, .wav, .m4a


Project Smeargle is a command line utility that is designed to detect if your music files are missing artwork. If they are, PS will send an API call to a locally hosted Stable Diffusion instance to generate some artwork. After image generation, the image will (optionally) be processed to include the artist and song title. This processed image will then be saved as a cover.png file alongside the music file, with image tags and a watermark to indicate that it is AI generated. 


Once the image is saved and the process is finished, most music players will be able to detect the new album artwork and will display it alongside the music. 


# BEFORE AND AFTER:

![abstractum - miss u (before and after)](https://github.com/user-attachments/assets/7b7c5308-0279-4a41-803b-3710bcc0ac65)
![Satl   Malaky - Loneliness (before and after)](https://github.com/user-attachments/assets/b97132a4-105a-4e51-a35a-41a7706e343d)



# Setup Guide:
## Prerequisites: 
1. Download and setup the Stable Diffusion application with the API enabled
	- See SD documentation at https://github.com/AUTOMATIC1111/stable-diffusion-webui
2. Download and install Python
   	- Be sure to select "add to PATH" during installation
   	- Python will be installed by default on most Linux distros
3. Download and install Git
   	- On windows, in CMD enter ```winget install Git.Git```
   		- Restart CMD
   	- Git will be installed by default on most Linux Distros
   
## Linux/Ubuntu Setup:
1. Clone the repository
   
   ```git clone https://github.com/ShiningLava/project_smeargle.git```
2. Install python virtual environment
   
   ```apt install python3-venv```
3. Change directory and initialize the virtual environment
   
   ```cd project_smeargle```
   
   ```python3 -m venv venv```
   
   ```source venv/bin/activate```
4. Install the requirements
   
    ```pip install -r requirements.txt```
5. Edit `config.json` and change `music_directory` and `stable_diffusion_url`
   
    ```nano config.json```
	
6. Run the script

    ```python smeargle.py```
	

## Windows Setup:
### The following commands will be entered in CMD.exe
1. Clone the repository into the desired directory
   
   ```cd C:\Users\[USER]\Desktop``` 
   
   ```git clone https://github.com/ShiningLava/project_smeargle.git```
3. Change directory and initialize the virtual environment
   
   ```cd project_smeargle```
   
   ```python -m venv venv```

   ```venv\Scripts\activate.bat```
4. Install the requirements
   
    ```pip install -r requirements.txt```
5. Edit the config file and change `music_directory` and `stable_diffusion_url`
   
    - In Windows, this can easily be done by selecting `config.json` and opening it in Notepad (or text editor of your choice)
	
6. Run the script

    ```python smeargle.py```

# USAGE:

Use the config file to pass defaults
```python3 smeargle.py --config config.json```

Use a custom prompt
```python3 smeargle.py --prompt "enter custom prompt here"```

Scan a different `music_directory` and regenerate previously made cover.pngs
```python3 smeargle.py --music_directory /path/to/music/directory --regenerate_ai_images true```

Target songs in a random order and limit the script to only scan 50 songs (useful for automation and overnight tasks)
Edit `config.json` and set `random_selection_enabled` to`true`
```python3 smeargle.py --config config.json --image_limit 50```

# FAQ:

Q: Is this going to delete or ruin my current artwork? Or corrupt my music?

A: No. PS is designed to not write anything to your music files directly. PS will read your music files to check their artist, title, and artwork tags, however, PS should never delete or modify any existing data on the music files themselves. Instead, PS will generate a cover.png file for any music it determines to not have artwork. Always make sure you have a backup of important data before running unknown scripts from the internet.


Q: How do I set up Stable Diffusion? 

A: See Stable Diffusion documentation: `https://github.com/AUTOMATIC1111/stable-diffusion-webui`


Q: How do I enable the Stable Diffusion API?

A: Once you have Stable Diffusion set up locally, you can edit the `webui-user.bat` file to include "--api" in the `COMMANDLINE_ARGS`. Once you reload the Stable Diffusion application, the API should be exposed. You can confirm the API is exposed by going to `http://<stable_diffusion_ip>:7860/docs` in a web browser. If Stable Diffusion is hosted on the same machine, you can go to the loopback address at `http://127.0.0.1:7860/docs`



Q: How do I get rid of the images made by this script?

A: Run the `Cover_Image_Remover.py` script. It's recommended to set `dry_run_enabled` = `true` in `config.json` file first to test the script. Once you are satisfied with the results printed in the console, set `dry_run_enabled` = `false` in `config.json` and run the script again to actually delete PS images.



Q: I ran `smeargle.py` but I didn't get any artwork with my music. What gives?

A: Check `config.json` file and double check `dry_run_enabled` and `test_folder_enabled`. `Dry_run_enabled` will skip generating art and the `test_folder_enabled` will generate art, but will save them at /project_smeargle/test_image_output instead of saving them with the music file.



Q: Why the space theme for the Stable Diffusion prompt?

A: Space is an easy theme for SD to produce as it's easy to hide simple AI mistakes, as well as generally making images that aren't ugly to look at. If you feel like you can make better prompts, feel free to run `smeargle.py` with the `--prompt ""` flag!



Q: Can I change the parameters of the API call?

A: Currently this must be done in the `smeargle.py` script instead of `config.json`. This can be found in the function `sd_api_call`. If you would like to adjust these settings, please see the example in the Stable Diffusion txt2img API documentation at `http://<stable_diffusion_ip>:7860/docs#/default/text2imgapi_sdapi_v1_txt2img_post`. 



Q: Your code sucks?

A: Yes. 

