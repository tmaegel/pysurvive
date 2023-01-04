#!/usr/bin/env python
# coding=utf-8
from typing import Union

import pygame as pg
import pytiled_parser as pytiled

from pysurvive.config import ROOT_PATH
from pysurvive.logger import Logger
from pysurvive.utils import load_image

logger = Logger()


class Tileset:

    """Represents and load a tileset from filesystem."""

    def __init__(self, _config: pytiled.tileset.Tileset) -> None:
        self.config = _config
        self.table = self._load(self.tileset_path, self.tile_width, self.tile_height)

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

    def get_tile(self, tile_id: int) -> pg.surface.Surface:
        """Returns the tile (image) by id."""
        return self.table[tile_id - self.first_gid]

    @staticmethod
    def _load(
        tileset_file: str, tile_width: int, tile_height: int
    ) -> list[pg.surface.Surface]:
        """
        Load a tileset from single file and split it into a table.
        The tileset consists of several tiles arranged in a row.
        """
        logger.info("Loading tileset from file %s.", tileset_file)
        image, _ = load_image(tileset_file, alpha=True)
        image_width, image_height = image.get_size()
        tile_table: list[pg.surface.Surface] = []
        for tile_x in range(0, image_width // tile_width):
            rect = (
                tile_x * tile_width,
                0,
                tile_width,
                tile_height,
            )
            # Subsurface doesn’t create copies in memory.
            tile_image = image.subsurface(rect)
            tile_table.append(tile_image)

        return tile_table
