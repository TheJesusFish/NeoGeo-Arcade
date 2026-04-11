#!/usr/bin/env python3
"""
Neo Geo MGL Generator
---------------------
Generates a MGL file and MVS-mode CFG for a .neo ROM file.
Output files are placed in the same folder as the input .neo file.

Usage:
    python3 generate_neogeo_mgl.py <path/to/game.neo> [game2.neo ...]
"""

import os
import re
import sys

# CFG bytes: MVS (byte 0 = 0x02), crop in byte 2 (0x00=320, 0x01=304)
CFG_MVS_320 = bytes([0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
CFG_MVS_304 = bytes([0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00,
                     0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
CFG_MVS_NONE = bytes([0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])


def rel_path_from_neo(neo_path):
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
    display_name = filename[:-4]
    rel = rel_path_from_neo(neo_path)

    print(f"\nFile    : {filename}")
    print(f"Display : {display_name}")

    setname = input("Setname : ").strip()
    if not setname:
        print("ERROR: Setname cannot be empty.")
        return False

    while True:
        crop = input("Crop    : [320 / 304 / none] ").strip().lower()
        if crop in ('320', '304', 'none', ''):
            break
        print("         Please enter 320, 304, or none.")

    # MGL
    mgl_content = f'''<mistergamedescription>
    <rbf>_Console/NeoGeo</rbf>
    <setname same_dir="1">{setname}</setname>
    <file delay="1" type="f" index="1" path="{rel}"/>
</mistergamedescription>
'''
    mgl_path = os.path.join(folder, f'{display_name}.mgl')
    with open(mgl_path, 'w') as f:
        f.write(mgl_content)
    print(f"✓ MGL   : {mgl_path}")

    # CFG
    if crop == '304':
        cfg_bytes = CFG_MVS_304
    elif crop == '320':
        cfg_bytes = CFG_MVS_320
    else:
        cfg_bytes = CFG_MVS_NONE

    cfg_path = os.path.join(folder, f'{setname}.CFG')
    with open(cfg_path, 'wb') as f:
        f.write(cfg_bytes)
    print(f"✓ CFG   : {cfg_path}")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    for neo in sys.argv[1:]:
        generate(neo)
        print()
