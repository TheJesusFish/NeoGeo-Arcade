#!/usr/bin/env python3
"""
Neo Geo MGL Generator
---------------------
Generates a MGL file and MVS-mode CFG for a .neo ROM file.
Output files are placed in the same folder as the input .neo file.

Usage:
    python3 generate_neogeo_mgl.py <path/to/game.neo>
"""

import os
import sys

# MVS-mode CFG content (16 bytes, byte 0x02 = MVS mode)
MVS_CFG_BYTES = bytes([0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                       0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])


def rel_path_from_neo(neo_path):
    """
    Extract the path relative to the NEOGEO games folder.
    E.g. /Volumes/MiSTer/games/NEOGEO/1 World A-Z/mygame.neo
    becomes 1 World A-Z/mygame.neo
    """
    parts = os.path.normpath(neo_path).split(os.sep)
    try:
        idx = next(i for i, p in enumerate(parts) if p.upper() == 'NEOGEO')
        return os.path.join(*parts[idx + 1:])
    except StopIteration:
        return os.path.basename(neo_path)


def generate(neo_path):
    neo_path = os.path.abspath(neo_path)

    if not neo_path.lower().endswith('.neo'):
        print(f"ERROR: '{neo_path}' is not a .neo file.")
        return False
    if not os.path.isfile(neo_path):
        print(f"ERROR: File not found: '{neo_path}'")
        return False

    folder = os.path.dirname(neo_path)
    filename = os.path.basename(neo_path)
    display_name = filename[:-4]  # strip .neo
    rel = rel_path_from_neo(neo_path)

    print(f"\nFile    : {filename}")
    print(f"Display : {display_name}")
    setname = input("Setname : ").strip()

    if not setname:
        print("ERROR: Setname cannot be empty.")
        return False

    mgl_content = f'''<mistergamedescription>
    <rbf>_Console/NeoGeo</rbf>
    <setname same_dir="1">{setname}</setname>
    <file delay="1" type="f" index="1" path="{rel}"/>
</mistergamedescription>
'''

    mgl_path = os.path.join(folder, f'{display_name}.mgl')
    with open(mgl_path, 'w') as f:
        f.write(mgl_content)

    cfg_path = os.path.join(folder, f'{setname}.CFG')
    with open(cfg_path, 'wb') as f:
        f.write(MVS_CFG_BYTES)

    print(f"✓ Created: {mgl_path}")
    print(f"✓ Created: {cfg_path}")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    for neo in sys.argv[1:]:
        generate(neo)
        print()
