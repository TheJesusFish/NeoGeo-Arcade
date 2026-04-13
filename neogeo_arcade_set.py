#!/usr/bin/env python3
"""
Neo Geo MGL Generator
Place this script in your NEOGEO games folder and run it.
Usage: python3 neogeo_arcade.py
"""

import os
import re
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# CFG bytes: MVS mode (byte 0 = 0x02), crop (byte 2: 0x00=320, 0x01=304)
# ---------------------------------------------------------------------------
CFG_MVS_320  = bytes([0x02,0x00,0x00,0x00,0x00,0x02,0x00,0x00,
                      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
CFG_MVS_304  = bytes([0x02,0x00,0x01,0x00,0x00,0x02,0x00,0x00,
                      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
CFG_MVS_NONE = bytes([0x02,0x00,0x00,0x00,0x00,0x02,0x00,0x00,
                      0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])

# ---------------------------------------------------------------------------
# MAME database: setname -> (parent, display_name)
# parent == 'neogeo' means it is a top-level parent ROM
# ---------------------------------------------------------------------------
MAME_DB = {
    "2020bb":     ("neogeo",   "2020 Super Baseball (set 1)"),
    "2020bba":    ("2020bb",   "2020 Super Baseball (set 2)"),
    "2020bbh":    ("2020bb",   "2020 Super Baseball (set 3)"),
    "3countb":    ("neogeo",   "3 Count Bout"),
    "alpham2":    ("neogeo",   "Alpha Mission II"),
    "alpham2p":   ("alpham2",  "Alpha Mission II (prototype)"),
    "androdun":   ("neogeo",   "Andro Dunos"),
    "aodk":       ("neogeo",   "Aggressors of Dark Kombat"),
    "aof":        ("neogeo",   "Art of Fighting"),
    "aof2":       ("neogeo",   "Art of Fighting 2"),
    "aof2a":      ("aof2",     "Art of Fighting 2 (NGH-056)"),
    "aof3":       ("neogeo",   "Art of Fighting 3"),
    "aof3k":      ("aof3",     "Art of Fighting 3 (Korean)"),
    "b2b":        ("neogeo",   "Bang Bang Busters"),
    "bakatono":   ("neogeo",   "Bakatonosama Mahjong Manyuuki"),
    "bangbead":   ("neogeo",   "Bang Bead"),
    "bjourney":   ("neogeo",   "Blue's Journey"),
    "bjourneyh":  ("bjourney", "Blue's Journey (NGH-001)"),
    "blazstar":   ("neogeo",   "Blazing Star"),
    "breakers":   ("neogeo",   "Breakers"),
    "breakrev":   ("neogeo",   "Breakers Revenge"),
    "bstars":     ("neogeo",   "Baseball Stars Professional"),
    "bstars2":    ("neogeo",   "Baseball Stars 2"),
    "bstarsh":    ("bstars",   "Baseball Stars Professional (NGH-002)"),
    "burningf":   ("neogeo",   "Burning Fight"),
    "burningfh":  ("burningf", "Burning Fight (NGH-018, US)"),
    "burningfp":  ("burningf", "Burning Fight (prototype, older)"),
    "burningfpa": ("burningf", "Burning Fight (prototype, near final)"),
    "burningfpb": ("burningf", "Burning Fight (prototype, newer)"),
    "crswd2bl":   ("neogeo",   "Crossed Swords 2"),
    "crsword":    ("neogeo",   "Crossed Swords"),
    "ct2k3sa":    ("kof2001",  "Crouching Tiger Hidden Dragon 2003 Super Plus (alt)"),
    "ct2k3sp":    ("kof2001",  "Crouching Tiger Hidden Dragon 2003 Super Plus"),
    "cthd2003":   ("kof2001",  "Crouching Tiger Hidden Dragon 2003"),
    "ctomaday":   ("neogeo",   "Captain Tomaday"),
    "cyberlip":   ("neogeo",   "Cyber-Lip"),
    "diggerma":   ("neogeo",   "Digger Man (prototype)"),
    "doubledr":   ("neogeo",   "Double Dragon"),
    "dragonsh":   ("neogeo",   "Dragon's Heaven"),
    "eightman":   ("neogeo",   "Eight Man"),
    "fatfursp":   ("neogeo",   "Fatal Fury Special"),
    "fatfurspa":  ("fatfursp", "Fatal Fury Special (set 2)"),
    "fatfury1":   ("neogeo",   "Fatal Fury - King of Fighters"),
    "fatfury2":   ("neogeo",   "Fatal Fury 2"),
    "fatfury3":   ("neogeo",   "Fatal Fury 3"),
    "fbfrenzy":   ("neogeo",   "Football Frenzy"),
    "fightfev":   ("neogeo",   "Fight Fever"),
    "fightfeva":  ("fightfev", "Fight Fever (set 2)"),
    "flipshot":   ("neogeo",   "Battle Flip Shot"),
    "froman2b":   ("neogeo",   "Idol Mahjong Final Romance 2"),
    "fswords":    ("samsho3",  "Fighters Swords (Korean)"),
    "galaxyfg":   ("neogeo",   "Galaxy Fight"),
    "ganryu":     ("neogeo",   "Ganryu"),
    "garou":      ("neogeo",   "Garou - Mark of the Wolves"),
    "garoubl":    ("garou",    "Garou - Mark of the Wolves (bootleg)"),
    "garouh":     ("garou",    "Garou - Mark of the Wolves (NGM-2530 ~ NGH-2530)"),
    "garouha":    ("garou",    "Garou - Mark of the Wolves (NGH-2530)"),
    "garoup":     ("garou",    "Garou - Mark of the Wolves (prototype)"),
    "ghostlop":   ("neogeo",   "Ghostlop (prototype)"),
    "goalx3":     ("neogeo",   "Goal! Goal! Goal!"),
    "gowcaizr":   ("neogeo",   "Voltage Fighter - Gowcaizer"),
    "gpilots":    ("neogeo",   "Ghost Pilots"),
    "gpilotsh":   ("gpilots",  "Ghost Pilots (NGH-020, US)"),
    "gpilotsp":   ("gpilots",  "Ghost Pilots (prototype)"),
    "gururin":    ("neogeo",   "Gururin"),
    "ironclad":   ("neogeo",   "Iron Clad (prototype)"),
    "ironclado":  ("ironclad", "Iron Clad (prototype, bootleg)"),
    "irrmaze":    ("neogeo",   "Irritating Maze, The"),
    "janshin":    ("neogeo",   "Janshin Densetsu"),
    "jockeygp":   ("neogeo",   "Jockey Grand Prix"),
    "jockeygpa":  ("jockeygp", "Jockey Grand Prix (set 2)"),
    "joyjoy":     ("neogeo",   "Joy Joy Kid"),
    "kabukikl":   ("neogeo",   "Kabuki Klash"),
    "karnovr":    ("neogeo",   "Karnov's Revenge"),
    "kf10thep":   ("kof2002",  "King of Fighters 10th Anniversary Extra Plus, The"),
    "kf2k2mp":    ("kof2002",  "King of Fighters 2002 Magic Plus, The"),
    "kf2k2mp2":   ("kof2002",  "King of Fighters 2002 Magic Plus II, The"),
    "kf2k2pla":   ("kof2002",  "King of Fighters 2002 Plus, The (set 2)"),
    "kf2k2pls":   ("kof2002",  "King of Fighters 2002 Plus, The (set 1)"),
    "kf2k3bl":    ("kof2003",  "King of Fighters 2003, The (bootleg set 1)"),
    "kf2k3bla":   ("kof2003",  "King of Fighters 2003, The (bootleg set 2)"),
    "kf2k3pcb":   ("kof2003",  "King of Fighters 2003, The (JAMMA PCB)"),
    "kf2k3pl":    ("kof2003",  "King of Fighters 2004 Plus - Hero, The"),
    "kf2k3upl":   ("kof2003",  "King of Fighters 2004 Ultra Plus, The"),
    "kf2k5uni":   ("kof2002",  "King of Fighters 10th Anniversary 2005 Unique, The"),
    "kizuna":     ("neogeo",   "Kizuna Encounter"),
    "kizuna4p":   ("kizuna",   "Kizuna Encounter (4 Way Battle)"),
    "kof10th":    ("kof2002",  "King of Fighters 10th Anniversary, The"),
    "kof2000":    ("neogeo",   "King of Fighters 2000, The"),
    "kof2000n":   ("kof2000",  "King of Fighters 2000, The (not encrypted)"),
    "kof2001":    ("neogeo",   "King of Fighters 2001, The"),
    "kof2001h":   ("kof2001",  "King of Fighters 2001, The (NGH-2621)"),
    "kof2002":    ("neogeo",   "King of Fighters 2002, The"),
    "kof2002b":   ("kof2002",  "King of Fighters 2002, The (bootleg)"),
    "kof2003":    ("neogeo",   "King of Fighters 2003, The"),
    "kof2003h":   ("kof2003",  "King of Fighters 2003, The (NGH-2710)"),
    "kof2k4se":   ("kof2002",  "King of Fighters Special Edition 2004, The"),
    "kof94":      ("neogeo",   "King of Fighters '94, The"),
    "kof95":      ("neogeo",   "King of Fighters '95, The"),
    "kof95a":     ("kof95",    "King of Fighters '95, The (alt board)"),
    "kof95h":     ("kof95",    "King of Fighters '95, The (NGH-084)"),
    "kof96":      ("neogeo",   "King of Fighters '96, The"),
    "kof96a":     ("kof96",    "King of Fighters '96, The (bug fix)"),
    "kof96h":     ("kof96",    "King of Fighters '96, The (NGH-214)"),
    "kof97":      ("neogeo",   "King of Fighters '97, The"),
    "kof97h":     ("kof97",    "King of Fighters '97, The (NGH-2320)"),
    "kof97k":     ("kof97",    "King of Fighters '97, The (Korean)"),
    "kof97oro":   ("kof97",    "King of Fighters '97 Chongchu Jianghu Plus 2003"),
    "kof97pls":   ("kof97",    "King of Fighters '97 Plus, The"),
    "kof98":      ("neogeo",   "King of Fighters '98, The"),
    "kof98a":     ("kof98",    "King of Fighters '98, The (alt board)"),
    "kof98h":     ("kof98",    "King of Fighters '98, The (NGH-2420)"),
    "kof98k":     ("kof98",    "King of Fighters '98, The (Korean set 1)"),
    "kof98ka":    ("kof98",    "King of Fighters '98, The (Korean set 2)"),
    "kof99":      ("neogeo",   "King of Fighters '99, The"),
    "kof99e":     ("kof99",    "King of Fighters '99, The (earlier)"),
    "kof99h":     ("kof99",    "King of Fighters '99, The (NGH-2510)"),
    "kof99k":     ("kof99",    "King of Fighters '99, The (Korean)"),
    "kof99ka":    ("kof99",    "King of Fighters '99, The (Korean, non-encrypted)"),
    "kof99p":     ("kof99",    "King of Fighters '99, The (prototype)"),
    "kog":        ("kof97",    "King of Gladiator"),
    "kotm":       ("neogeo",   "King of the Monsters (set 1)"),
    "kotm2":      ("neogeo",   "King of the Monsters 2"),
    "kotm2a":     ("kotm2",    "King of the Monsters 2 (older)"),
    "kotm2p":     ("kotm2",    "King of the Monsters 2 (prototype)"),
    "kotmh":      ("kotm",     "King of the Monsters (set 2)"),
    "lans2004":   ("shocktr2", "Lansquenet 2004"),
    "lastblad":   ("neogeo",   "Last Blade, The"),
    "lastbladh":  ("lastblad", "Last Blade, The (NGH-2340)"),
    "lastbld2":   ("neogeo",   "Last Blade 2, The"),
    "lasthope":   ("neogeo",   "Last Hope"),
    "lastsold":   ("lastblad", "Last Soldier, The"),
    "lbowling":   ("neogeo",   "League Bowling"),
    "legendos":   ("neogeo",   "Legend of Success Joe"),
    "lresort":    ("neogeo",   "Last Resort"),
    "lresortp":   ("lresort",  "Last Resort (prototype)"),
    "magdrop2":   ("neogeo",   "Magical Drop II"),
    "magdrop3":   ("neogeo",   "Magical Drop III"),
    "maglord":    ("neogeo",   "Magician Lord"),
    "maglordh":   ("maglord",  "Magician Lord (NGH-005)"),
    "mahretsu":   ("neogeo",   "Mahjong Kyo Retsuden"),
    "marukodq":   ("neogeo",   "Chibi Marukochan Deluxe Quiz"),
    "matrim":     ("neogeo",   "Matrimelee"),
    "matrimbl":   ("matrim",   "Matrimelee (bootleg)"),
    "miexchng":   ("neogeo",   "Money Idol Exchanger"),
    "minasan":    ("neogeo",   "Minasan no Okagesamadesu!"),
    "moshougi":   ("neogeo",   "Master of Shougi"),
    "ms4plus":    ("mslug4",   "Metal Slug 4 Plus (bootleg)"),
    "ms5pcb":     ("mslug5",   "Metal Slug 5 (JAMMA PCB)"),
    "ms5plus":    ("mslug5",   "Metal Slug 5 Plus (bootleg)"),
    "mslug":      ("neogeo",   "Metal Slug - Super Vehicle-001"),
    "mslug2":     ("neogeo",   "Metal Slug 2 - Super Vehicle-001-II"),
    "mslug2t":    ("mslug2",   "Metal Slug 2 Turbo"),
    "mslug3":     ("neogeo",   "Metal Slug 3"),
    "mslug3a":    ("mslug3",   "Metal Slug 3 (earlier)"),
    "mslug3b6":   ("mslug3",   "Metal Slug 6 (bootleg of Metal Slug 3)"),
    "mslug3h":    ("mslug3",   "Metal Slug 3 (NGH-2560)"),
    "mslug4":     ("neogeo",   "Metal Slug 4"),
    "mslug4h":    ("mslug4",   "Metal Slug 4 (NGH-2630)"),
    "mslug5":     ("neogeo",   "Metal Slug 5"),
    "mslug5b":    ("mslug5",   "Metal Slug 5 (bootleg)"),
    "mslug5h":    ("mslug5",   "Metal Slug 5 (NGH-2680)"),
    "mslugx":     ("neogeo",   "Metal Slug X"),
    "mutnat":     ("neogeo",   "Mutation Nation"),
    "nam1975":    ("neogeo",   "NAM-1975"),
    "ncombat":    ("neogeo",   "Ninja Combat"),
    "ncombath":   ("ncombat",  "Ninja Combat (NGH-009)"),
    "ncommand":   ("neogeo",   "Ninja Commando"),
    "neobombe":   ("neogeo",   "Neo Bomberman"),
    "neocup98":   ("neogeo",   "Neo-Geo Cup '98"),
    "neodrift":   ("neogeo",   "Neo Drift Out"),
    "neomrdo":    ("neogeo",   "Neo Mr. Do!"),
    "ninjamas":   ("neogeo",   "Ninja Master's"),
    "nitd":       ("neogeo",   "Nightmare in the Dark"),
    "nitdbl":     ("nitd",     "Nightmare in the Dark (bootleg)"),
    "overtop":    ("neogeo",   "Over Top"),
    "panicbom":   ("neogeo",   "Panic Bomber"),
    "pbobbl2n":   ("neogeo",   "Puzzle Bobble 2"),
    "pbobblen":   ("neogeo",   "Puzzle Bobble"),
    "pbobblenb":  ("pbobblen", "Puzzle Bobble (bootleg)"),
    "pgoal":      ("neogeo",   "Pleasure Goal"),
    "pnyaa":      ("neogeo",   "Pochi and Nyaa"),
    "pnyaaa":     ("pnyaa",    "Pochi and Nyaa (Ver 2.00)"),
    "popbounc":   ("neogeo",   "Pop 'n Bounce - Gapporin"),
    "preisle2":   ("neogeo",   "Prehistoric Isle 2"),
    "pspikes2":   ("neogeo",   "Power Spikes II"),
    "pulstar":    ("neogeo",   "Pulstar"),
    "puzzldpr":   ("neogeo",   "Puzzle De Pon! R!"),
    "puzzledp":   ("neogeo",   "Puzzle De Pon!"),
    "quizdai2":   ("neogeo",   "Quiz Daisousa Sen Part 2"),
    "quizdais":   ("neogeo",   "Quiz Daisousa Sen"),
    "quizdaisk":  ("quizdais", "Quiz Daisousa Sen (Korean)"),
    "quizkof":    ("neogeo",   "Quiz King of Fighters"),
    "quizkofk":   ("quizkof",  "Quiz King of Fighters (Korean)"),
    "ragnagrd":   ("neogeo",   "Ragnagard"),
    "rbff1":      ("neogeo",   "Real Bout Fatal Fury"),
    "rbff1a":     ("rbff1",    "Real Bout Fatal Fury (bugfix)"),
    "rbff1k":     ("rbff1",    "Real Bout Fatal Fury (Korean)"),
    "rbff1ka":    ("rbff1",    "Real Bout Fatal Fury (Korean, bugfix)"),
    "rbff2":      ("neogeo",   "Real Bout Fatal Fury 2"),
    "rbff2h":     ("rbff2",    "Real Bout Fatal Fury 2 (NGH-2400)"),
    "rbff2k":     ("rbff2",    "Real Bout Fatal Fury 2 (Korean)"),
    "rbffspec":   ("neogeo",   "Real Bout Fatal Fury Special"),
    "rbffspeck":  ("rbffspec", "Real Bout Fatal Fury Special (Korean)"),
    "ridhero":    ("neogeo",   "Riding Hero"),
    "ridheroh":   ("ridhero",  "Riding Hero (set 2)"),
    "roboarma":   ("roboarmy", "Robo Army (Alt)"),
    "roboarmy":   ("neogeo",   "Robo Army"),
    "roboarmya":  ("roboarmy", "Robo Army (NGM-032 ~ NGH-032)"),
    "rotd":       ("neogeo",   "Rage of the Dragons"),
    "rotdh":      ("rotd",     "Rage of the Dragons (NGH-2640)"),
    "s1945p":     ("neogeo",   "Strikers 1945 Plus"),
    "samsh5sp":   ("neogeo",   "Samurai Shodown V Special"),
    "samsh5sph":  ("samsh5sp", "Samurai Shodown V Special (NGH-2720, less censored)"),
    "samsh5spho": ("samsh5sp", "Samurai Shodown V Special (NGH-2720, censored)"),
    "samsho":     ("neogeo",   "Samurai Shodown"),
    "samsho2":    ("neogeo",   "Samurai Shodown II"),
    "samsho2k":   ("samsho2",  "Samurai Shodown II (Korean set 1)"),
    "samsho2ka":  ("samsho2",  "Samurai Shodown II (Korean set 2)"),
    "samsho3":    ("neogeo",   "Samurai Shodown III"),
    "samsho3h":   ("samsho3",  "Samurai Shodown III (NGH-087)"),
    "samsho4":    ("neogeo",   "Samurai Shodown IV"),
    "samsho4k":   ("samsho4",  "Samurai Shodown IV (Korean)"),
    "samsho5":    ("neogeo",   "Samurai Shodown V"),
    "samsho5a":   ("samsho5",  "Samurai Shodown V (set 2)"),
    "samsho5b":   ("samsho5",  "Samurai Shodown V (bootleg)"),
    "samsho5h":   ("samsho5",  "Samurai Shodown V (NGH-2700)"),
    "samshoh":    ("samsho",   "Samurai Shodown (NGH-045)"),
    "savagere":   ("neogeo",   "Savage Reign"),
    "sbp":        ("neogeo",   "Super Bubble Pop"),
    "sdodgeb":    ("neogeo",   "Super Dodge Ball"),
    "sengoku":    ("neogeo",   "Sengoku"),
    "sengoku2":   ("neogeo",   "Sengoku 2"),
    "sengoku3":   ("neogeo",   "Sengoku 3"),
    "sengoku3a":  ("sengoku3", "Sengoku 3 (set 2)"),
    "sengokuh":   ("sengoku",  "Sengoku (NGH-017, US)"),
    "shocktr2":   ("neogeo",   "Shock Troopers 2"),
    "shocktro":   ("neogeo",   "Shock Troopers (set 1)"),
    "shocktroa":  ("shocktro", "Shock Troopers (set 2)"),
    "socbrawl":   ("neogeo",   "Soccer Brawl"),
    "socbrawlh":  ("socbrawl", "Soccer Brawl (NGH-031)"),
    "sonicwi2":   ("neogeo",   "Aero Fighters 2"),
    "sonicwi3":   ("neogeo",   "Aero Fighters 3"),
    "spinmast":   ("neogeo",   "Spin Master"),
    "ssideki":    ("neogeo",   "Super Sidekicks"),
    "ssideki2":   ("neogeo",   "Super Sidekicks 2"),
    "ssideki3":   ("neogeo",   "Super Sidekicks 3"),
    "ssideki4":   ("neogeo",   "Super Sidekicks 4"),
    "stakwin":    ("neogeo",   "Stakes Winner"),
    "stakwin2":   ("neogeo",   "Stakes Winner 2"),
    "strhoop":    ("neogeo",   "Street Hoop"),
    "superspy":   ("neogeo",   "Super Spy, The"),
    "svc":        ("neogeo",   "SNK vs. Capcom"),
    "svcboot":    ("svc",      "SNK vs. Capcom (bootleg)"),
    "svcpcb":     ("svc",      "SNK vs. Capcom (JAMMA PCB, set 1)"),
    "svcpcba":    ("svc",      "SNK vs. Capcom (JAMMA PCB, set 2)"),
    "svcplus":    ("svc",      "SNK vs. Capcom Plus (bootleg set 1)"),
    "svcplusa":   ("svc",      "SNK vs. Capcom Plus (bootleg set 2)"),
    "svcsplus":   ("svc",      "SNK vs. Capcom Super Plus (bootleg)"),
    "tophuntr":   ("neogeo",   "Top Hunter"),
    "tophuntrh":  ("tophuntr", "Top Hunter (NGH-046)"),
    "tpgolf":     ("neogeo",   "Top Player's Golf"),
    "trally":     ("neogeo",   "Thrash Rally"),
    "turfmast":   ("neogeo",   "Neo Turf Masters"),
    "twinspri":   ("neogeo",   "Twinkle Star Sprites"),
    "twsoc96":    ("neogeo",   "Tecmo World Soccer '96"),
    "tws96":      ("neogeo",   "Tecmo World Soccer '96"),
    "viewpoin":   ("neogeo",   "Viewpoint"),
    "viewpoinp":  ("viewpoin", "Viewpoint (prototype)"),
    "vliner":     ("neogeo",   "V-Liner"),
    "vliner53":   ("vliner",   "V-Liner (v0.53)"),
    "vliner54":   ("vliner",   "V-Liner (v0.54)"),
    "vliner6e":   ("vliner",   "V-Liner (v0.6e)"),
    "vliner7e":   ("vliner",   "V-Liner (v0.7e)"),
    "vlinero":    ("vliner",   "V-Liner (set 2)"),
    "wakuwak7":   ("neogeo",   "Waku Waku 7"),
    "wh1":        ("neogeo",   "World Heroes"),
    "wh1h":       ("wh1",      "World Heroes (NGH-005)"),
    "wh1ha":      ("wh1",      "World Heroes (set 3)"),
    "wh2":        ("neogeo",   "World Heroes 2"),
    "wh2h":       ("wh2",      "World Heroes 2 (NGH-006)"),
    "wh2j":       ("neogeo",   "World Heroes 2 Jet"),
    "whp":        ("neogeo",   "World Heroes Perfect"),
    "wjammers":   ("neogeo",   "Windjammers"),
    "zedblade":   ("neogeo",   "Zed Blade"),
    "zintrckb":   ("neogeo",   "Zintrick"),
    "zupapa":     ("neogeo",   "Zupapa!"),
}

# ---------------------------------------------------------------------------
# Crop resolution sets — keyed by MAME setname
# ---------------------------------------------------------------------------
CROP_320 = {
    '3countb', 'sonicwi2', 'sonicwi3', 'aof3', 'aof3k',
    'bstars', 'bstars2', 'bstarsh', 'blazstar', 'bjourney', 'bjourneyh',
    'breakers', 'breakrev', 'marukodq', 'cyberlip', 'doubledr', 'eightman',
    'fatfursp', 'fatfurspa', 'fatfury1', 'fatfury2', 'fatfury3', 'fbfrenzy',
    'garou', 'garoubl', 'garouh', 'garouha', 'garoup',
    'ghostlop', 'ironclad', 'ironclado',
    'janshin', 'kabukikl',
    'lastblad', 'lastbladh', 'lastsold', 'lastbld2',
    'maglord', 'maglordh', 'mahretsu', 'matrim', 'matrimbl', 'moshougi',
    'nam1975', 'neocup98', 'nitd', 'nitdbl', 'ninjamas', 'ncombat', 'ncombath',
    'panicbom', 'pbobblen', 'pbobblenb', 'pspikes2', 'pulstar',
    'quizdais', 'quizdaisk', 'quizdai2',
    'ragnagrd',
    'rbff1', 'rbff1a', 'rbff1k', 'rbff1ka',
    'rbff2', 'rbff2h', 'rbff2k',
    'rbffspec', 'rbffspeck',
    'ridhero', 'ridheroh', 'rotd', 'rotdh',
    'samsho', 'samshoh', 'samsho2', 'samsho2k', 'samsho2ka',
    'samsho4', 'samsho4k',
    'samsho5', 'samsho5a', 'samsho5b', 'samsho5h',
    'samsh5sp', 'samsh5sph', 'samsh5spho',
    's1945p',
    'sengoku', 'sengokuh', 'sengoku2', 'sengoku3', 'sengoku3a',
    'stakwin', 'stakwin2',
    'ssideki', 'ssideki2', 'ssideki3', 'ssideki4',
    'superspy', 'tophuntr', 'tophuntrh', 'tpgolf', 'trally',
    'wh1', 'wh1h', 'wh1ha', 'whp',
    'diggerma', 'dragonsh',  # prototypes — defaulting to 320
}

CROP_304 = {
    '2020bb', '2020bba', '2020bbh',
    'aodk', 'alpham2', 'alpham2p', 'androdun',
    'aof', 'aof2', 'aof2a',
    'b2b', 'bakatono', 'bangbead',
    'burningf', 'burningfh', 'burningfp', 'burningfpa', 'burningfpb',
    'crsword', 'crswd2bl',
    'ct2k3sa', 'ct2k3sp', 'cthd2003', 'ctomaday',
    'fightfev', 'fightfeva', 'flipshot', 'froman2b', 'fswords',
    'galaxyfg', 'ganryu', 'goalx3',
    'gpilots', 'gpilotsh', 'gpilotsp',
    'gowcaizr', 'gururin', 'irrmaze',
    'jockeygp', 'jockeygpa', 'joyjoy', 'karnovr',
    'kf10thep', 'kf2k2mp', 'kf2k2mp2', 'kf2k2pla', 'kf2k2pls',
    'kf2k3bl', 'kf2k3bla', 'kf2k3pcb', 'kf2k3pl', 'kf2k3upl', 'kf2k5uni',
    'kizuna', 'kizuna4p', 'kof10th',
    'kof2000', 'kof2000n', 'kof2001', 'kof2001h',
    'kof2002', 'kof2002b', 'kof2003', 'kof2003h', 'kof2k4se',
    'kof94',
    'kof95', 'kof95a', 'kof95h',
    'kof96', 'kof96a', 'kof96h',
    'kof97', 'kof97h', 'kof97k', 'kof97oro', 'kof97pls',
    'kof98', 'kof98a', 'kof98h', 'kof98k', 'kof98ka',
    'kof99', 'kof99e', 'kof99h', 'kof99k', 'kof99ka', 'kof99p',
    'kog', 'kotm', 'kotmh', 'kotm2', 'kotm2a', 'kotm2p',
    'lans2004', 'lbowling', 'legendos', 'lresort', 'lresortp',
    'magdrop2', 'magdrop3', 'miexchng', 'minasan',
    'ms4plus', 'ms5pcb', 'ms5plus',
    'mslug', 'mslug2', 'mslug2t',
    'mslug3', 'mslug3a', 'mslug3b6', 'mslug3h',
    'mslug4', 'mslug4h', 'mslug5', 'mslug5b', 'mslug5h', 'mslugx',
    'mutnat', 'ncommand', 'neobombe', 'neodrift', 'neomrdo', 'overtop',
    'pgoal', 'pnyaa', 'pnyaaa', 'pbobbl2n', 'popbounc', 'preisle2',
    'puzzledp', 'puzzldpr', 'quizkof', 'quizkofk',
    'roboarmy', 'roboarma', 'roboarmya',
    'samsho3', 'samsho3h', 'savagere', 'sbp', 'sdodgeb',
    'shocktro', 'shocktroa', 'shocktr2',
    'socbrawl', 'socbrawlh', 'spinmast', 'strhoop',
    'svc', 'svcboot', 'svcpcb', 'svcpcba', 'svcplus', 'svcplusa', 'svcsplus',
    'turfmast', 'twinspri', 'tws96', 'twsoc96',
    'viewpoin', 'viewpoinp',
    'vliner', 'vliner53', 'vliner54', 'vliner6e', 'vliner7e', 'vlinero',
    'wakuwak7', 'wh2', 'wh2h', 'wh2j', 'wjammers',
    'zedblade', 'zintrckb', 'zupapa',
}

# ---------------------------------------------------------------------------
# Non-arcade games — processed separately with their own prompt
# ---------------------------------------------------------------------------
NON_ARCADE = {
    'lasthope',  # AES to MVS bootleg, no coin support
    'totc',      # AES only, freeplay on MVS
    'columnsn',  # Homebrew Columns port, not in MAME
    'neofight',  # Not in MAME
    'lasthpcd',  # Last Hope CD homebrew, not in MAME
}

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def normalize(s):
    """Lowercase, strip punctuation, collapse spaces."""
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', '', s.lower())).strip()


def strip_parens(name):
    """Strip all trailing parentheticals."""
    while True:
        s = re.sub(r'\s*\([^)]*\)\s*$', '', name).strip()
        if s == name:
            break
        name = s
    return name


def the_prefix(name):
    """Move trailing ', The' to a leading 'The '."""
    if name.endswith(', The'):
        return 'The ' + name[:-5]
    return name


def safe_filename(name):
    """Make a name safe for use as a filename."""
    return name.replace('/', '-').replace('\\', '-').replace(':', '-')


def display_from_desc(desc):
    """Convert a MAME description to a menu display name."""
    return the_prefix(desc)


def folder_name(desc):
    """Convert a MAME description to an _alternatives folder name."""
    return safe_filename(the_prefix(strip_parens(desc)))


def get_crop(sn):
    """Return '320', '304', or None based on setname."""
    if sn in CROP_320:
        return '320'
    if sn in CROP_304:
        return '304'
    return None


def extract_setname(filepath):
    """
    Extract setname from filename.
    .neo: extract trailing (setname) parenthetical.
    .zip/.rom: stem is the setname.
    """
    stem = os.path.splitext(os.path.basename(filepath))[0]
    ext  = os.path.splitext(filepath)[1].lower()
    if ext == '.neo':
        m = re.match(r'^.+\s+\(([^)]+)\)$', stem)
        return m.group(1) if m else None
    return stem


def prompt(question, options=None, default=None):
    """Simple prompt with validation."""
    while True:
        suffix = ''
        if options:
            suffix = ' [' + '/'.join(options) + ']'
        if default:
            suffix += f' (default: {default})'
        ans = input(f'{question}{suffix}: ').strip()
        if not ans and default:
            return default
        if options and ans.lower() not in options:
            print(f'  Please enter one of: {", ".join(options)}')
            continue
        return ans.lower() if options else ans


def _build_reverse_lookup():
    """Normalized desc -> (setname, parent) for inferring parents of unknown ROMs."""
    lookup = {}
    for sn, (parent, desc) in MAME_DB.items():
        norm = normalize(desc)
        lookup[norm] = (sn, parent)
        if norm.endswith(' the'):
            lookup[norm[:-4].strip()] = (sn, parent)
    return lookup


MAME_BY_DESC = _build_reverse_lookup()


def infer_parent(display):
    """
    Try to infer parent setname and display from a display name by stripping
    trailing parentheticals, then trailing words one at a time.
    Returns (parent_setname, parent_display) or (None, None).
    """
    def lookup(name):
        norm = normalize(name)
        if norm in MAME_BY_DESC:
            sn, _ = MAME_BY_DESC[norm]
            return sn, display_from_desc(MAME_DB[sn][1])
        return None, None

    base = display
    while True:
        stripped = re.sub(r'\s*\([^)]*\)\s*$', '', base).strip()
        if stripped == base:
            break
        base = stripped
        sn, pd = lookup(base)
        if sn:
            return sn, pd

    words = base.split()
    for i in range(1, min(5, len(words))):
        candidate = ' '.join(words[:-i])
        if not candidate:
            break
        sn, pd = lookup(candidate)
        if sn:
            return sn, pd

    return None, None


def ask_unknown(filepath, base_dir):
    """
    Prompt user for details about an unknown ROM, inferring what we can.
    Returns (display, setname, crop, is_alt, parent_display).
    Returns (None, ...) for exit, ('', ...) for skip.
    """
    filename = os.path.basename(filepath)
    stem     = os.path.splitext(filename)[0]
    ext      = os.path.splitext(filename)[1].lower()

    inferred_display = None
    inferred_setname = None
    if ext == '.neo':
        m = re.match(r'^(.+)\s+\(([^)]+)\)$', stem)
        if m:
            inferred_display = m.group(1).strip()
            inferred_setname = m.group(2).strip()
    else:
        inferred_setname = stem

    print(f'\n  ⚠️  Unknown ROM: {filename}')
    print(f'  (enter "skip" to skip, "exit" to stop)\n')

    if inferred_display:
        print(f'  Display name  : {inferred_display}')
        display = inferred_display
    else:
        raw = input('  Display name  : ').strip()
        if raw.lower() == 'exit': return None, None, None, None, None
        if raw.lower() == 'skip': return '',   None, None, None, None
        display = raw

    if inferred_setname:
        print(f'  Setname       : {inferred_setname}')
        setname = inferred_setname
    else:
        raw = input('  Setname       : ').strip()
        if raw.lower() == 'exit': return None, None, None, None, None
        if raw.lower() == 'skip': return '',   None, None, None, None
        setname = raw

    crop = get_crop(setname) if setname else None
    if crop:
        print(f'  Crop          : {crop}')
    else:
        crop = prompt('  Crop', ['320', '304', 'none'])

    inferred_parent_sn, inferred_parent_display = infer_parent(display)
    if inferred_parent_sn:
        print(f'  Clone of      : {inferred_parent_display}')
        is_alt         = True
        parent_display = inferred_parent_display
    else:
        is_alt = prompt('  Is this an alternative/clone?', ['y', 'n']) == 'y'
        parent_display = None
        if is_alt:
            parent_display = input('  Parent game name (for folder): ').strip()

    return display, setname, crop, is_alt, parent_display


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f'\n🎮 Neo Geo MGL Generator')
    print(f'   Folder: {base_dir}\n')

    # Step 1: Find top-level folders, ask about exclusions
    top_dirs = sorted([
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
        and not d.startswith('.')
        and d != 'NeoGeo MGLs'
    ])

    if not top_dirs:
        print('No subfolders found. Exiting.')
        sys.exit(0)

    print('Found these folders:')
    for i, d in enumerate(top_dirs):
        print(f'  {i+1}. {d}')

    print('\nEnter numbers of folders to EXCLUDE (comma-separated), or press Enter to include all:')
    excl_input = input('  Exclude: ').strip()
    excluded = set()
    if excl_input:
        for part in excl_input.split(','):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(top_dirs):
                    excluded.add(top_dirs[idx])
    if excluded:
        print(f'  Excluding: {", ".join(sorted(excluded))}')

    # Step 2: Collect all ROM files
    rom_exts = {'.neo', '.zip', '.rom'}
    all_files = []
    for root, dirs, files in os.walk(base_dir):
        rel_root = os.path.relpath(root, base_dir)
        top = rel_root.split(os.sep)[0]
        if top in excluded:
            dirs.clear()
            continue
        if rel_root == '.':
            continue
        for f in files:
            if os.path.splitext(f)[1].lower() in rom_exts:
                all_files.append(os.path.join(root, f))

    print(f'\nFound {len(all_files)} ROM files.')

    # Step 3: Extract setnames, detect duplicates
    setname_map   = defaultdict(list)
    unknown_files = []

    for fp in all_files:
        sn = extract_setname(fp)
        if sn:
            setname_map[sn].append(fp)
        else:
            unknown_files.append(fp)

    # Step 4: Resolve duplicates
    duplicates = {sn: paths for sn, paths in setname_map.items() if len(paths) > 1}
    if duplicates:
        print(f'\n⚠️  Found {len(duplicates)} duplicate setname(s):')

    for sn, paths in list(duplicates.items()):
        print(f'\n  Setname "{sn}" appears in multiple files:')
        for i, fp in enumerate(paths):
            print(f'    {i+1}. {os.path.relpath(fp, base_dir)}')
        options = [str(i+1) for i in range(len(paths))] + ['both']
        choice = prompt(
            '  Which is the main version? (number, or "both" to treat all as new entries)',
            options
        )
        if choice == 'both':
            for fp in paths:
                unknown_files.append(fp)
            del setname_map[sn]
        else:
            main_fp = paths[int(choice) - 1]
            setname_map[sn] = [main_fp]
            for fp in paths:
                if fp != main_fp:
                    unknown_files.append(fp)

    # Step 5: Set up output directories
    out_base   = os.path.join(base_dir, 'NeoGeo MGLs')
    out_arcade = os.path.join(out_base, '_Arcade')
    out_alt    = os.path.join(out_arcade, '_alternatives')
    out_cfg    = os.path.join(out_base, 'config')

    already_done = set()
    if os.path.exists(out_base):
        if prompt('Output folder already exists. Resume where you left off?', ['y', 'n']) == 'y':
            if os.path.exists(out_cfg):
                already_done = {
                    os.path.splitext(f)[0]
                    for f in os.listdir(out_cfg)
                    if f.endswith('.CFG')
                }
            print(f'  Resuming — {len(already_done)} game(s) already completed.')
        else:
            import shutil
            shutil.rmtree(out_base)

    os.makedirs(out_arcade, exist_ok=True)
    os.makedirs(out_alt,    exist_ok=True)
    os.makedirs(out_cfg,    exist_ok=True)

    stats = {'auto': 0, 'prompted_crop': 0, 'unknown': 0, 'skipped': 0}

    def write_mgl(mgl_dir, display, setname, rel_path):
        os.makedirs(mgl_dir, exist_ok=True)
        mgl_path = os.path.join(mgl_dir, f'{safe_filename(display)}.mgl')
        with open(mgl_path, 'w') as f:
            f.write(
                f'<mistergamedescription>\n'
                f'    <rbf>_Console/NeoGeo</rbf>\n'
                f'    <setname same_dir="1">{setname}</setname>\n'
                f'    <file delay="1" type="f" index="1" path="{rel_path}"/>\n'
                f'</mistergamedescription>\n'
            )

    def write_cfg(setname, crop):
        data = CFG_MVS_320 if crop == '320' else CFG_MVS_304 if crop == '304' else CFG_MVS_NONE
        with open(os.path.join(out_cfg, f'{setname}.CFG'), 'wb') as f:
            f.write(data)

    def process_known(fp, sn):
        entry = MAME_DB.get(sn)
        if not entry:
            return False
        if sn in already_done:
            return True

        parent, desc = entry
        display  = display_from_desc(desc)
        is_clone = parent != 'neogeo'
        crop     = get_crop(sn)

        if crop is None:
            print(f'\n  ❓ No crop entry for: {display}')
            crop = prompt('  Crop', ['320', '304', 'none'])
            stats['prompted_crop'] += 1
        else:
            stats['auto'] += 1

        rel = os.path.relpath(fp, base_dir)

        if is_clone:
            parent_desc = MAME_DB[parent][1] if parent in MAME_DB else parent
            write_mgl(os.path.join(out_alt, f'_{folder_name(parent_desc)}'), display, sn, rel)
        else:
            write_mgl(out_arcade, display, sn, rel)

        write_cfg(sn, crop)
        print(f'  ✓ {display} [{crop}]')
        return True

    # Step 6: Separate arcade vs non-arcade
    arcade_map          = {}
    non_arcade_map      = {}
    non_arcade_unknowns = []
    arcade_unknowns     = []

    for sn, paths in setname_map.items():
        if sn in NON_ARCADE:
            non_arcade_map[sn] = paths
        else:
            arcade_map[sn] = paths

    for fp in unknown_files:
        sn = extract_setname(fp)
        if sn and sn in NON_ARCADE:
            non_arcade_unknowns.append(fp)
        else:
            arcade_unknowns.append(fp)

    # Step 7: Process arcade ROMs
    print(f'\nProcessing arcade ROMs...\n')
    for sn, paths in arcade_map.items():
        if not process_known(paths[0], sn):
            arcade_unknowns.append(paths[0])

    # Step 8: Non-arcade prompt
    all_non_arcade = list(non_arcade_map.items()) + [(None, [fp]) for fp in non_arcade_unknowns]
    if all_non_arcade:
        print(f'\n{len(all_non_arcade)} non-arcade game(s) found.')
        if prompt('Process non-arcade games?', ['y', 'n']) == 'y':
            print()
            for sn, paths in non_arcade_map.items():
                if not process_known(paths[0], sn):
                    arcade_unknowns.append(paths[0])
            for fp in non_arcade_unknowns:
                display, sn, crop, is_alt, parent_display = ask_unknown(fp, base_dir)
                if not display or not sn:
                    stats['skipped'] += 1
                    continue
                rel = os.path.relpath(fp, base_dir)
                dest = os.path.join(out_alt, f'_{folder_name(parent_display)}') if is_alt and parent_display else out_arcade
                write_mgl(dest, display, sn, rel)
                write_cfg(sn, crop)
                print(f'  ✓ {display} [{crop}]')
                stats['unknown'] += 1

    # Step 9: Unknown games prompt
    if arcade_unknowns:
        print(f'\n{len(arcade_unknowns)} game(s) not in this script\'s database.')
        if prompt('Would you like to enter information for them now?', ['y', 'n']) == 'y':
            print()
            for fp in arcade_unknowns:
                display, sn, crop, is_alt, parent_display = ask_unknown(fp, base_dir)
                if display is None:
                    print('\nExiting.')
                    break
                if display == '' or not sn:
                    stats['skipped'] += 1
                    continue
                rel = os.path.relpath(fp, base_dir)
                dest = os.path.join(out_alt, f'_{folder_name(parent_display)}') if is_alt and parent_display else out_arcade
                write_mgl(dest, display, sn, rel)
                write_cfg(sn, crop)
                print(f'  ✓ {display} [{crop}]')
                stats['unknown'] += 1

    # Summary
    print(f'\n✅ Done!')
    print(f'   Auto-processed  : {stats["auto"]}')
    print(f'   Prompted (crop) : {stats["prompted_crop"]}')
    print(f'   Manual entry    : {stats["unknown"]}')
    print(f'   Skipped         : {stats["skipped"]}')
    print(f'   Output          : {out_base}')


if __name__ == '__main__':
    main()
