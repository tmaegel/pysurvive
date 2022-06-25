#!/usr/bin/env python
# coding=utf-8
from enum import Enum, unique

import pygame as pg

from pysurvive.config import COLORKEY, TILE_SIZE
from pysurvive.logger import logger
from pysurvive.utils import load_image


@unique
class TileIndex(Enum):

    """Represents the index (x, y) of a single tile the tile table."""

    TOP_LEFT = (0, 0)
    TOP = (1, 0)
    TOP_RIGHT = (2, 0)
    LEFT = (0, 1)
    MIDDLE = (1, 1)
    RIGHT = (2, 1)
    BOTTOM_LEFT = (0, 2)
    BOTTOM = (1, 2)
    BOTTOM_RIGHT = (2, 2)
    INNER_BOTTOM_RIGHT = (3, 0)
    INNER_BTTOM_LEFT = (4, 0)
    INNER_TOP_RIGHT = (3, 1)
    INNER_TOP_LEFT = (4, 1)
    # (3, 2) and (4, 2) are unset!

    @property
    def tile(self) -> tuple[int, int]:
        return self.value


class Tileset:

    """Represents and load a tileset from filesystem."""

    def __init__(self, _name: str, _filename: str) -> None:
        self.name = _name
        self.filename = _filename
        self.enter = False  # Player can not enter this tile.
        self.block = False  # This tile block e.g. bullets.
        self.table = self._load(self.filename)  # Single tiles in a 2d-table.

    def __str__(self) -> str:
        return f"{self.name}={self.filename}"

    def _load(self, filename: str, tile_size: int = TILE_SIZE) -> list[list[pg.Rect]]:
        """Load a tileset from filename and split it into a table."""
        logger.info("Loading tileset from file %s.", filename)
        image, _ = load_image(filename, alpha=True)
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width // tile_size):
            line: list[pg.Surface] = []
            tile_table.append(line)
            for tile_y in range(0, image_height // tile_size):
                rect = (tile_x * tile_size, tile_y * tile_size, tile_size, tile_size)
                # Subsurface doesn’t create copies in memory.
                tile_image = image.subsurface(rect)
                if tile_image.get_at((0, 0)) == COLORKEY:
                    line.append(None)
                else:
                    line.append(tile_image)

        return tile_table
