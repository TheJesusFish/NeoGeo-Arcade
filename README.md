# NeoGeo Arcade MGLs
This is a set of NeoGeo MGL files for the MiSTer FPGA Arcade folder. The companion config files use the `setname` string from the MGL in order to set the Unibios to Arcade and use the preferred crop as noted by FirebrandX [here](https://drive.google.com/file/d/1ieshu26TAHAZqSRXpCWYBntr-eIHSJBK/view?usp=drivesdk).

## Installation
Unzip the zip file into the `/media/fat` folder of your SD Card/NAS/USB drive. It will place the MGLs in the /_Arcade folder (including any alternatives) and it will place all the .cfg files in the /config folder.

## Known Issues
- **Fatal Fury 3** errors on first load. Selecting **Reset & Apply** from the MiSTer OSD will cause it to load correctly.

## FAQ
### Do I need the config files?
No, the games will run from the /_Arcade folder without the config files. However, the config files are set up so that the games load in MVS mode (regardless as to what you have your NeoGeo core set to).
### I don't see [Game X].
This set is based on the HTGDB NeoGeo set, so it won't have the most recent games. I've included a script that you can use to generate an MGL and .cfg file based on any roms not already included.
