#!/usr/bin/env python
# coding=utf-8
"""
Example map file:

[level]
default_tileset = ground
map = ::......................
      ::......................
      .....::::.......||......
      .....::::.......||||....
      .....::::.........||....
      ........................
      ...........___..........
      ...........___..........

[.]
name = ground
tileset = assets/img/tiles/ground/tilelist.png

[:]
name = grass
tileset = assets/img/tiles/grass/tilelist.png

[|]
name = wall
tileset = assets/img/tiles/wall/tilelist.png
enter = true
block = true

[|]
name = water
tileset = assets/img/tiles/water/tilelist.png
enter = true
"""

import configparser
from typing import Optional

import pygame as pg

from pysurvive.config import TILE_SIZE, WHITE
from pysurvive.logger import logger
from pysurvive.map.tileset import TileIndex, Tileset


class Level(pg.sprite.Sprite):

    """Load a map file from disk and draw it on a surface."""

    def __init__(self, _game, _map_file: str) -> None:
        super().__init__()
        self.game = _game  # Reference to the game object.
        self.x = 0
        self.y = 0
        self.map_file = _map_file  # Filename (including path) of the map file.
        self.map_table_raw = []  # Map with contains each raw tile (from map file).
        # Contains infos about the tileset used in the map file
        # and the tileset itself. Loaded from map file.
        self.tilesets = {}
        self.default_tileset = None
        self.width = 500  # Map width (default). Overwrite by _load_map().
        self.height = 500  # Map height (default). Overwrite by _load_map().
        self._load(self.map_file)
        # Map size (width x height) based on the loaded map file.
        self.image = pg.Surface((self.width * TILE_SIZE, self.height * TILE_SIZE))
        self.image.fill(WHITE)
        self.rect = pg.Rect(
            self.x, self.y, self.width * TILE_SIZE, self.height * TILE_SIZE
        )
        self._render()

    def _initialize(self) -> None:
        """
        Initialize/convert the raw map table into a extra table that
        contains the determined tile indices. Prevents the recalculation
        of the map when it needs to be re-rendered
        """
        # @todo: Uses numpy.
        pass

    def _render(self) -> None:
        """Render initial the map on its own surface to blit it later at once."""
        # First render the default tileset. This is the default background.
        for y, row in enumerate(self.map_table_raw):
            for x, tile in enumerate(row):
                tile_x, tile_y = TileIndex.MIDDLE.tile
                self.image.blit(
                    self.default_tileset.table[tile_x][tile_y],
                    (x * TILE_SIZE, y * TILE_SIZE),
                )
        # Then render all map tiles unequal to the default tileset.
        for y, row in enumerate(self.map_table_raw):
            for x, tile in enumerate(row):
                if tile != self.default_tileset.sign:
                    used_tileset = self.tilesets[tile].table
                    tile_x, tile_y = self.get_tile_index(x, y, tile)
                    self.image.blit(
                        used_tileset[tile_x][tile_y], (x * TILE_SIZE, y * TILE_SIZE)
                    )

    def _load(self, map_file: str) -> None:
        """Load map from filesystem."""
        logger.info("Loading map from file %s.", map_file)
        parser = configparser.ConfigParser()
        # @todo: Exception for: Filename not exists.
        parser.read(map_file)
        # Get map key (map array) from map_file.
        self.map_table_raw = parser.get("level", "map").split("\n")
        default_tileset = parser.get("level", "default_tileset")
        for section in parser.sections():
            if len(section) == 1:
                desc = dict(parser.items(section))
                # @todo: set block and enter flag, if available!
                tileset = Tileset(desc["name"], section, desc["tileset"])
                self.tilesets[section] = tileset
                if desc["name"] == default_tileset:
                    logger.info("The default tileset is %s.", tileset)
                    self.default_tileset = tileset
        self.width = len(self.map_table_raw[0])
        self.height = len(self.map_table_raw)

    def update(self) -> None:
        """Update the map object."""
        self.rect.x = round(self.x - self.game.offset[0])
        self.rect.y = round(self.y - self.game.offset[1])

    def get_tile(self, x: int, y: int) -> Optional[str]:
        if x < 0 or y < 0:
            return None
        try:
            return self.map_table_raw[y][x]
        except IndexError:
            return None

    def get_tile_index(self, x: int, y: int, current: str) -> tuple[int, int]:
        """Get the right tile index for the tileset table epending on neighbourhood."""
        # @todo: Refactor this horrible function.
        # Check for map cornors.
        if (
            (
                not self.get_tile(x - 1, y - 1)
                and not self.get_tile(x - 1, y)
                and not self.get_tile(x, y - 1)
            )
            or (
                not self.get_tile(x + 1, y + 1)
                and not self.get_tile(x + 1, y)
                and not self.get_tile(x, y + 1)
            )
            or (
                not self.get_tile(x + 1, y - 1)
                and not self.get_tile(x + 1, y)
                and not self.get_tile(x, y - 1)
            )
            or (
                not self.get_tile(x - 1, y + 1)
                and not self.get_tile(x - 1, y)
                and not self.get_tile(x, y + 1)
            )
        ):
            return TileIndex.MIDDLE.tile

        if self.get_tile(x + 1, y) != current:  # Right
            # Check for outside of the map.
            if not self.get_tile(x, y - 1) or not self.get_tile(x, y + 1):
                return TileIndex.RIGHT.tile
            if (
                not self.get_tile(x + 1, y)
                and self.get_tile(x, y - 1) == current
                and self.get_tile(x, y + 1) == current
            ):
                return TileIndex.MIDDLE.tile
            # Check for outer cornors.
            if self.get_tile(x, y - 1) != current:
                if not self.get_tile(x + 1, y - 1):
                    return TileIndex.TOP.tile
                return TileIndex.TOP_RIGHT.tile
            if self.get_tile(x, y + 1) != current:
                if not self.get_tile(x + 1, y + 1):
                    return TileIndex.BOTTOM.tile
                return TileIndex.BOTTOM_RIGHT.tile
            return TileIndex.RIGHT.tile
        if self.get_tile(x - 1, y) != current:  # Left
            # Check for outside of the map.
            if not self.get_tile(x, y - 1) or not self.get_tile(x, y + 1):
                return TileIndex.LEFT.tile
            if (
                not self.get_tile(x - 1, y)
                and self.get_tile(x, y - 1) == current
                and self.get_tile(x, y + 1) == current
            ):
                return TileIndex.MIDDLE.tile
            # Check for outer cornors.
            if self.get_tile(x, y - 1) != current:
                if not self.get_tile(x - 1, y - 1):
                    return TileIndex.TOP.tile
                return TileIndex.TOP_LEFT.tile
            if self.get_tile(x, y + 1) != current:
                if not self.get_tile(x - 1, y + 1):
                    return TileIndex.BOTTOM.tile
                return TileIndex.BOTTOM_LEFT.tile
            return TileIndex.LEFT.tile
        if self.get_tile(x, y - 1) != current:  # Above
            # Check for outside of the map.
            if not self.get_tile(x, y - 1):
                return TileIndex.MIDDLE.tile
            return TileIndex.TOP.tile
        if self.get_tile(x, y + 1) != current:  # Below
            # Check for outside of the map.
            if not self.get_tile(x, y + 1):
                return TileIndex.MIDDLE.tile
            return TileIndex.BOTTOM.tile
        if self.get_tile(x + 1, y - 1) != current:  # Top right inner cornor.
            return TileIndex.INNER_TOP_RIGHT.tile
        if self.get_tile(x - 1, y - 1) != current:  # Top left inner cornor.
            return TileIndex.INNER_TOP_LEFT.tile
        if self.get_tile(x + 1, y + 1) != current:  # Bottom right inner cornor.
            return TileIndex.INNER_BOTTOM_RIGHT.tile
        if self.get_tile(x - 1, y + 1) != current:  # Bottom left inner cornor.
            return TileIndex.INNER_BTTOM_LEFT.tile

        # Default tile index
        return TileIndex.MIDDLE.tile
