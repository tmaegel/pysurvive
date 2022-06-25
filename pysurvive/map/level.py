#!/usr/bin/env python
# coding=utf-8
"""
Example map file:

[level]
layer_0 = 0000000000
          0000000000
          0000000000
          0000000000
          0000000000
          0000000000
          0000000000
          0000000000
          0000000000
          0000000000
          0000000000
          0000000000

layer_1 = ...000....
          ...000....
          ...000....
          ...000....
          ..........
          ..........
          ..........
          ..........
          ...000....
          ...000....
          ...000....
          ..........

[stone]
layer = 0
tileset = assets/img/tiles/stone/tilelist.png
enter = false
block = false

[grass]
layer = 1
tileset = assets/img/tiles/grass/tilelist.png
enter = false
block = false
"""

import configparser
import re
from os.path import exists as file_exists
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
        # Character which shows that the tile is set at this position in the map.
        self.tile_flag = "0"
        self.x = 0
        self.y = 0
        self.map_file = _map_file  # Filename (including path) of the map file.
        self.map_layer_raw = (
            {}
        )  # Map layer with contains each raw tile (from map file).
        # Contains infos about the tileset used in the map file
        # and the tileset itself. Loaded from map file.
        self.tilesets = {}
        self.width = 1  # Map width (default). Overwrite by _load_map().
        self.height = 1  # Map height (default). Overwrite by _load_map().
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
        for layer_index, layer_desc in self.map_layer_raw.items():
            try:
                used_tileset = self.tilesets[layer_index].table
            except KeyError:
                logger.warning("Missing tileset fo layer %s.", layer_index)
                continue
            for y, row in enumerate(layer_desc):
                for x, tile in enumerate(row):
                    # Only render if the tile is set in layer description.
                    if tile == self.tile_flag:
                        # tile_x, tile_y = TileIndex.MIDDLE.tile
                        tile_x, tile_y = self.get_tile_index(layer_index, x, y)
                        self.image.blit(
                            used_tileset[tile_x][tile_y],
                            (x * TILE_SIZE, y * TILE_SIZE),
                        )

    def _load(self, map_file: str) -> None:
        """Load map from filesystem."""
        logger.info("Loading map from file %s.", map_file)
        if not file_exists(map_file):
            logger.error("Map file %s does not exists.", map_file)
            return

        last_layer = None
        map_config = configparser.ConfigParser()
        map_config.read(map_file)

        # Read the layer of the map file.
        for layer_name, layer_desc in map_config["level"].items():
            regex_result = re.search("^layer_(?P<layer_index>[0-9]+)$", layer_name)
            if not regex_result:
                continue
            layer_index = regex_result.groupdict()["layer_index"]
            if layer_index:
                last_layer = layer_index
                self.map_layer_raw[int(layer_index)] = layer_desc.split("\n")

        # Read and load the tileset defined in the map file.
        for section in map_config.sections():
            desc = dict(map_config.items(section))
            if "tileset" not in desc or "layer" not in desc:
                continue
            # @todo: set block and enter flag, if available!
            tileset = Tileset(section, desc["tileset"])
            # @todo: Map config validity check: integer, ...
            self.tilesets[int(desc["layer"])] = tileset

        if last_layer:
            # Get map size based in the last layer.
            self.width = len(self.map_layer_raw[int(layer_index)][0])
            self.height = len(self.map_layer_raw[int(layer_index)])

    def update(self) -> None:
        """Update the map object."""
        self.rect.x = round(self.x - self.game.offset[0])
        self.rect.y = round(self.y - self.game.offset[1])

    def get_tile(self, layer_index: int, x: int, y: int) -> Optional[str]:
        if x < 0 or y < 0:
            return None
        try:
            return self.map_layer_raw[layer_index][y][x]
        except IndexError:
            return None

    def get_tile_index(self, layer_index: int, x: int, y: int) -> tuple[int, int]:
        """Get the right tile index for the tileset table epending on neighbourhood."""
        # Check for map cornors.
        if (
            (
                not self.get_tile(layer_index, x - 1, y - 1)
                and not self.get_tile(layer_index, x - 1, y)
                and not self.get_tile(layer_index, x, y - 1)
            )
            or (
                not self.get_tile(layer_index, x + 1, y + 1)
                and not self.get_tile(layer_index, x + 1, y)
                and not self.get_tile(layer_index, x, y + 1)
            )
            or (
                not self.get_tile(layer_index, x + 1, y - 1)
                and not self.get_tile(layer_index, x + 1, y)
                and not self.get_tile(layer_index, x, y - 1)
            )
            or (
                not self.get_tile(layer_index, x - 1, y + 1)
                and not self.get_tile(layer_index, x - 1, y)
                and not self.get_tile(layer_index, x, y + 1)
            )
        ):
            return TileIndex.MIDDLE.tile

        # RIGHT
        if self.get_tile(layer_index, x + 1, y) != self.tile_flag:
            # Check for outside of the map.
            if not self.get_tile(layer_index, x, y - 1) or not self.get_tile(
                layer_index, x, y + 1
            ):
                return TileIndex.RIGHT.tile
            if (
                not self.get_tile(layer_index, x + 1, y)
                and self.get_tile(layer_index, x, y - 1) == self.tile_flag
                and self.get_tile(layer_index, x, y + 1) == self.tile_flag
            ):
                return TileIndex.MIDDLE.tile
            # Check for outer cornors.
            if self.get_tile(layer_index, x, y - 1) != self.tile_flag:
                if not self.get_tile(layer_index, x + 1, y - 1):
                    return TileIndex.TOP.tile
                return TileIndex.TOP_RIGHT.tile
            if self.get_tile(layer_index, x, y + 1) != self.tile_flag:
                if not self.get_tile(layer_index, x + 1, y + 1):
                    return TileIndex.BOTTOM.tile
                return TileIndex.BOTTOM_RIGHT.tile
            return TileIndex.RIGHT.tile

        # LEFT
        if self.get_tile(layer_index, x - 1, y) != self.tile_flag:
            # Check for outside of the map.
            if not self.get_tile(layer_index, x, y - 1) or not self.get_tile(
                layer_index, x, y + 1
            ):
                return TileIndex.LEFT.tile
            if (
                not self.get_tile(layer_index, x - 1, y)
                and self.get_tile(layer_index, x, y - 1) == self.tile_flag
                and self.get_tile(layer_index, x, y + 1) == self.tile_flag
            ):
                return TileIndex.MIDDLE.tile
            # Check for outer cornors.
            if self.get_tile(layer_index, x, y - 1) != self.tile_flag:
                if not self.get_tile(layer_index, x - 1, y - 1):
                    return TileIndex.TOP.tile
                return TileIndex.TOP_LEFT.tile
            if self.get_tile(layer_index, x, y + 1) != self.tile_flag:
                if not self.get_tile(layer_index, x - 1, y + 1):
                    return TileIndex.BOTTOM.tile
                return TileIndex.BOTTOM_LEFT.tile
            return TileIndex.LEFT.tile

        # Check for sides of the map.
        if (
            not self.get_tile(layer_index, x + 1, y)
            or not self.get_tile(layer_index, x - 1, y)
            or not self.get_tile(layer_index, x, y + 1)
            or not self.get_tile(layer_index, x, y - 1)
        ):
            return TileIndex.MIDDLE.tile

        # ABOVE
        if self.get_tile(layer_index, x, y - 1) != self.tile_flag:
            return TileIndex.TOP.tile

        # BELOW
        if self.get_tile(layer_index, x, y + 1) != self.tile_flag:
            return TileIndex.BOTTOM.tile

        # Top right inner cornor.
        if self.get_tile(layer_index, x + 1, y - 1) != self.tile_flag:
            return TileIndex.INNER_TOP_RIGHT.tile

        # Top left inner cornor.
        if self.get_tile(layer_index, x - 1, y - 1) != self.tile_flag:
            return TileIndex.INNER_TOP_LEFT.tile

        # Bottom right inner cornor.
        if self.get_tile(layer_index, x + 1, y + 1) != self.tile_flag:
            return TileIndex.INNER_BOTTOM_RIGHT.tile

        # Bottom left inner cornor.
        if self.get_tile(layer_index, x - 1, y + 1) != self.tile_flag:
            return TileIndex.INNER_BTTOM_LEFT.tile

        return TileIndex.MIDDLE.tile
