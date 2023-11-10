#!/usr/bin/env python
# coding=utf-8
from typing import Any

import pytiled_parser as pytiled

from pysurvive.config import ROOT_PATH
from pysurvive.logger import Logger
from pysurvive.map.tile import Tile
from pysurvive.utils import load_image

logger = Logger()


class Tileset:

    """Represents and load a tileset from filesystem."""

    def __init__(self, _config: pytiled.tileset.Tileset) -> None:
        self.config = _config
        self.tile_table: list[Tile] = self._load()

    def __str__(self) -> str:
        return (
            f"Tileset (name={self.name},"
            f" tile_size={self.tile_width}x{self.tile_height},"
            f" ids=[{self.first_gid} .. {self.last_gid}]"
        )

    def _load(self) -> list[Tile]:
        """
        Load a tileset from single file and split it into a tile_table.
        The tileset consists of several tiles arranged in a row.
        """
        logger.info("Loading tileset from file %s.", self.tileset_file)
        tileset_image, _ = load_image(self.tileset_file, alpha=True)
        tileset_width, _ = tileset_image.get_size()
        tile_table: list[Tile] = []
        for tile_x in range(0, tileset_width // self.tile_width):
            rect = (
                tile_x * self.tile_width,
                0,
                self.tile_width,
                self.tile_height,
            )
            # Subsurface doesn’t create copies in memory.
            tile_image = tileset_image.subsurface(rect)

            tile = Tile(
                image=tile_image,
                enter=self.get_property("enter"),
                block=self.get_property("block"),
            )
            tile_table.append(tile)

        return tile_table

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
    def tileset_file(self) -> str:
        """Returns the tileset file (including path)."""
        return str(ROOT_PATH) + "/" + str(self.config.image)

    @property
    def first_gid(self) -> int:
        """Returns the first_gid (pytiled_parser specific)."""
        return self.config.firstgid

    @property
    def last_gid(self) -> int:
        """Returns the last_gid (pytiled_parser specific)."""
        return self.config.firstgid + (self.config.tile_count - 1)

    @property
    def tile_width(self) -> int:
        """Returns tile width in pixel."""
        return self.config.tile_width

    @property
    def tile_height(self) -> int:
        """Returns tile height in pixel."""
        return self.config.tile_height

    @property
    def properties(self) -> dict[str, Any]:
        if self.config.properties:
            return self.config.properties
        else:
            return {}

    def get_property(self, name: str) -> Any:
        """Returns the property value from `name`."""
        for prop_name, prop_value in self.properties.items():
            try:
                if prop_name == name:
                    return prop_value
            except AttributeError:
                return None

    def get_tile_index(self, tile_id: int) -> int:
        """Returns the tile index of the tile_table by id."""
        return tile_id - self.first_gid

    def get_tile(self, tile_id: int) -> Tile:
        """Returns the tile object by id."""
        return self.tile_table[tile_id - self.first_gid]
