#!/usr/bin/env python
# coding=utf-8
from pathlib import Path

import pygame as pg

# Logging
DEBUG_LOG = False

# Directories
ROOT_PATH = Path(__file__).parent
ASSETS_DIR = "assets"
MAP_DIR = "maps"
IMAGE_DIR = ASSETS_DIR + "/img"
SOUND_DIR = ASSETS_DIR + "/sound"

# Game settings
FPS = 30  # Frame per seconds
SCREEN_RECT = pg.Rect(0, 0, 1200, 800)
FLASHLIGHT_ENABLE = False

# Define the colors we will use in RGB format.
COLORKEY = (255, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (25, 25, 25)
GRAY_LIGHT = (172, 179, 192)
GRAY_LIGHT2 = (200, 200, 200)
GRAY_LIGHT3 = (225, 225, 225)
RED = (255, 0, 0)
RED_LIGHT = (224, 108, 117)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLUE_LIGHT = (97, 175, 239)
YELLOW = (255, 255, 0)
