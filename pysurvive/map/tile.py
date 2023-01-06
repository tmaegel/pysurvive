#!/usr/bin/env python
# coding=utf-8
import pygame as pg


class Tile(pg.sprite.Sprite):

    """Single tile object."""

    def __init__(
        self, tile_image: pg.surface.Surface, enter: bool = False, block: bool = False
    ) -> None:
        super().__init__()
        self.image = tile_image
        self.rect = self.image.get_rect()
        self.enter = enter
        self.block = block
