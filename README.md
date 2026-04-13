# NeoGeo Arcade MGL and Config Generator
This script will produce an entire set of MGLs and config files based on the roms in the directory in which it's run.

## Usage
Place the script in your `/media/fat/games/Neogeo` folder and run it via the `python3 neogeo_arcade_set.pw` command in the terminal of your choice.
The script will go through your neogeo directory (and sub directories) and detect your rom files.
- If the file exists in the MAME name database in the script, and it is an arcade game, it will 
  - Create an MGL file that matches your directory structure
  - Create a matching config file with the proper crop information and set the arcade flag
- If the file is in the DB and not an arcade game, it will ask you if you want to convert it
- If the file is not in the DB, it will ask if you want to do it manually where it will ask you
  - Game Name
  - Setname (you can make this up, it only matters for the config file)
  - Crop Info (320/304/none)
  - Whether or not it's a clone or a parent and, if it's a clone, the name of the parent
- If any games have duplicated set names, it will ask you set a new setname (and which one is the parent)

Once the script has finished running, you will find a `NeoGeo MGLs` folder in the folder you ran the script. Inside that folder is an `_Arcade` and `config` folder. You can copy those directly to /media/fat/, merging them with your existing directories.
 
## Known Issues
- **Fatal Fury 3** errors on first load. Selecting **Reset & Apply** from the MiSTer OSD will cause it to load correctly.

## FAQ
### Didn't this used to be a repository of MGLs and Config Files?
Yes, but the script is cleaner because it will use your folder structure instead of mine.

## Liner Notes
This script was written by an idea guy and a machine. If that bothers you, neither author gives a shit.
