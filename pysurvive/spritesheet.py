#!/usr/bin/env python
# coding=utf-8
import json

import pygame as pg

from pysurvive.config import COLORKEY
from pysurvive.utils import load_image


class Spritesheet:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.sprite_sheet, _ = load_image(filename, alpha=True, path=False)
        self.meta_data = self.filename.replace("png", "json")
        with open(self.meta_data) as f:
            self.data = json.load(f)
        f.close()

    def get_sprite(self, x, y, w, h):
        sprite = pg.Surface((w, h))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))

        return sprite

    def parse_sprite(self, index):
        sprite = self.data["frames"][index]["frame"]
        x, y, w, h = sprite["x"], sprite["y"], sprite["w"], sprite["h"]
        image = self.get_sprite(x, y, w, h)

        return image
