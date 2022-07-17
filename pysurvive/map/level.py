#!/usr/bin/env python
# coding=utf-8
import sys
from os.path import exists as file_exists
from pathlib import Path

import pygame as pg
import pytiled_parser as pytiled

from pysurvive.config import WHITE
from pysurvive.logger import logger
from pysurvive.map.tileset import Tileset


class Level(pg.sprite.Sprite):

    """Load a map file from disk and draw it on a surface."""

    def __init__(self, _game, _map_file: str) -> None:
        super().__init__()

        logger.info("Loading map from file %s.", _map_file)
        if not file_exists(_map_file):
            logger.error("Map file %s does not exists.", _map_file)
            sys.exit(1)

        self.game = _game  # Reference to the game object.
        # Character which shows that the tile is set at this position in the map.
        self.x = 0
        self.y = 0

        # Load map config
        self.map_file = Path(_map_file)
        self.map_config = pytiled.parse_map(self.map_file)
        self.map_width = (
            self.map_config.map_size.width * self.map_config.tile_size.width
        )
        self.map_height = (
            self.map_config.map_size.height * self.map_config.tile_size.height
        )

        # Load tilesets
        self.tilesets = {}
        for ts_id, ts_config in self.map_config.tilesets.items():
            tileset = Tileset(ts_config)
            self.tilesets[ts_id] = tileset

        # Create map sprite / image
        self.image = pg.Surface((self.map_width, self.map_height))
        self.image.fill(WHITE)
        self.rect = pg.Rect(self.x, self.y, self.map_width, self.map_height)

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
        # Render each layer of the tile map.
        for layer in self.map_config.layers:
            for y, row in enumerate(layer.data):
                for x, tile_id in enumerate(row):
                    tileset = self.get_tileset(tile_id)
                    if not tileset:
                        continue
                    tile_x, tile_y = tileset.get_tile(tile_id)
                    self.image.blit(
                        tileset.table[tile_x][tile_y],
                        (
                            x * self.map_config.tile_size.width,
                            y * self.map_config.tile_size.height,
                        ),
                    )

    def update(self) -> None:
        """Update the map object."""
        # @todo: Exctract only visible image (screen rect) from image
        # instead of moving the whole big map image.
        self.rect.x = round(self.x - self.game.offset[0])
        self.rect.y = round(self.y - self.game.offset[1])

    def get_tileset(self, tile_id: int) -> Tileset:
        """Identify the tileset based on the tile id specified in the map file."""
        for _, tileset in self.tilesets.items():
            if tile_id >= tileset.first_gid and tile_id <= tileset.last_gid:
                return tileset

        return None
