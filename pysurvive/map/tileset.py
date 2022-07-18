#!/usr/bin/env python
# coding=utf-8
from typing import Union

import pygame as pg
import pytiled_parser as pytiled

from pysurvive.config import COLORKEY, ROOT_PATH
from pysurvive.logger import logger
from pysurvive.utils import load_image


class Tileset:

    """Represents and load a tileset from filesystem."""

    def __init__(self, _config: pytiled.tileset.Tileset) -> None:
        self.config = _config
        # Check if the tileset is stored in a single file
        # or consists of mulitple files.
        _tileset_path = self.tileset_path
        self.table = self._load(_tileset_path)
        # Contains the images of the details for the tileset.
        # self.detail_images = self._load_details(f"{self.root_path}/details")

    def __str__(self) -> str:
        return (
            f"Tileset (name={self.name},"
            f" tile_size={self.tile_width}x{self.tile_height},"
            f" ids=[{self.first_gid} .. {self.last_gid}]"
        )

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def model(self) -> str:
        """
        Returns the model/type (e.g. ground, wall, floor, ...)
        of the tileset.
        """
        try:
            return self.config.properties["type"]
        except (KeyError, TypeError):
            return None

    @property
    def tileset_path(self) -> Union[str, list[str]]:
        """Returns the tileset path"""
        return str(ROOT_PATH) + "/" + str(self.config.image)

    @property
    def first_gid(self) -> int:
        return self.config.firstgid

    @property
    def last_gid(self) -> int:
        return self.config.firstgid + (self.config.tile_count - 1)

    @property
    def tile_width(self) -> int:
        return self.config.tile_width

    @property
    def tile_height(self) -> int:
        return self.config.tile_height

    def get_tile_index(self, tile_id: int) -> int:
        """Returns the tile index of the table by id."""
        return tile_id - self.first_gid

    def get_tile(self, tile_id: int) -> pg.Surface:
        """Returns the tile (image) by id."""
        return self.table[tile_id - self.first_gid]

    def _load(self, filename: str) -> list[list[pg.Surface]]:
        """Load a tileset from single filename and split it into a table."""
        logger.info("Loading tileset from file %s.", filename)
        image, _ = load_image(filename, alpha=True)
        image_width, image_height = image.get_size()
        tile_table: list[pg.Surface] = []
        for tile_x in range(0, image_width // self.tile_width):
            for tile_y in range(0, image_height // self.tile_height):
                rect = (
                    tile_x * self.tile_width,
                    tile_y * self.tile_height,
                    self.tile_width,
                    self.tile_height,
                )
                # Subsurface doesn’t create copies in memory.
                tile_image = image.subsurface(rect)
                if tile_image.get_at((0, 0)) == COLORKEY:
                    tile_table.append(None)
                else:
                    tile_table.append(tile_image)

        return tile_table
