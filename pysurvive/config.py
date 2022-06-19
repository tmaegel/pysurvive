#!/usr/bin/env python
# coding=utf-8
import pygame as pg

DEBUG_LOG = False

FLASHLIGHT_ENABLE = False

ASSETS_DIR = "assets"
IMAGE_DIR = ASSETS_DIR + "/img"
SOUND_DIR = ASSETS_DIR + "/sound"
SCREEN_RECT = pg.Rect(0, 0, 1600, 1000)

FPS = 30  # Frame per seconds

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
