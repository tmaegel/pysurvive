#!/usr/bin/env python
# coding=utf-8
import copy
import sys
from os.path import exists as file_exists
from pathlib import Path

import pygame as pg
import pytiled_parser as pytiled

from pysurvive.logger import Logger
from pysurvive.map.tileset import Tileset

logger = Logger()


class Level(pg.sprite.RenderPlain):

    """Load a map file from disk and draw it on a surface."""

    def __init__(self, _map_file: str) -> None:
        super().__init__()

        logger.info("Loading map from file %s.", _map_file)
        if not file_exists(_map_file):
            logger.error("Map file %s does not exists.", _map_file)
            sys.exit(1)

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

        self._initialize()

    def _initialize(self):
        """Initialize each layer of the tile map."""
        for layer in self.map_config.layers:
            # Exlude non TileLayer layers.
            if not isinstance(layer, pytiled.layer.TileLayer):
                continue

            for y, row in enumerate(layer.data):
                for x, tile_id in enumerate(row):
                    tileset = self.get_tileset(tile_id)
                    if not tileset:
                        continue

                    tile_index = tileset.get_tile_index(tile_id)
                    try:
                        tile = copy.deepcopy(tileset.get_tile(tile_id))
                        tile.x = x * self.map_config.tile_size.width
                        tile.y = y * self.map_config.tile_size.height
                        # Add a copy of tile from tileset.
                        self.add((tile,))
                    except IndexError:
                        logger.error(
                            "Error while accessing tile (%s) of tileset %r.",
                            tile_index,
                            tileset,
                        )
                        sys.exit(1)

    def get_tileset(self, tile_id: int) -> Tileset:
        """
        Identify the tileset based on the tile id specified
        in the map file.
        """
        for _, tileset in self.tilesets.items():
            if tile_id >= tileset.first_gid and tile_id <= tileset.last_gid:
                return tileset

        return None
