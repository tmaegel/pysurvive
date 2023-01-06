#!/usr/bin/env python
# coding=utf-8
import sys
from os.path import exists as file_exists
from pathlib import Path

import pygame as pg
import pytiled_parser as pytiled

from pysurvive.config import RED, WHITE
from pysurvive.game.core import Camera, Screen
from pysurvive.logger import Logger
from pysurvive.map.tileset import Tileset

logger = Logger()


class Level(pg.sprite.Sprite):

    """Load a map file from disk and draw it on a surface."""

    def __init__(self, _map_file: str) -> None:
        super().__init__()

        logger.info("Loading map from file %s.", _map_file)
        if not file_exists(_map_file):
            logger.error("Map file %s does not exists.", _map_file)
            sys.exit(1)

        self.screen = Screen()
        # Get camera module for the absolute position in the game world.
        self.camera = Camera()
        # Absolute map position.
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
        self.rect = pg.Rect(
            self.x + self.screen.centerx,
            self.y + self.screen.centery,
            self.map_width,
            self.map_height,
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
        """Render initial the map  on its own surface to blit it later at once."""
        # Render each layer of the tile map.
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
                        tile = tileset.get_tile(tile_id)
                        self.image.blit(
                            tile.image,
                            (
                                x * self.map_config.tile_size.width,
                                y * self.map_config.tile_size.height,
                            ),
                        )
                        # Draw debug border
                        if tile.enter:
                            pg.draw.rect(
                                self.image,
                                RED,
                                pg.Rect(
                                    x * self.map_config.tile_size.width,
                                    y * self.map_config.tile_size.height,
                                    tile.rect.width,
                                    tile.rect.height,
                                ),
                                width=1,
                            )
                    except IndexError:
                        logger.error(
                            "Error while accessing tile (%s) of tileset %r.",
                            tile_index,
                            tileset,
                        )
                        sys.exit(1)

        # for layer in self.map_config.layers:
        #     # Exlude non ObjectLayer layers.
        #     if not isinstance(layer, pytiled.layer.ObjectLayer):
        #         continue
        #
        #     for tile_obj in layer.tiled_objects:
        #         tileset = self.get_tileset(tile_obj.gid)
        #         if not tileset:
        #             continue
        #
        #         tile_index = tileset.get_tile_index(tile_obj.gid)
        #         try:
        #             tile = tileset.get_tile(tile_obj.gid)
        #             self.image.blit(
        #                 tile.image,
        #                 (tile_obj.coordinates.x, tile_obj.coordinates.y),
        #             )
        #         except IndexError:
        #             logger.error(
        #                 "Error while accessing tile (%s) of tileset %r.",
        #                 tile_index,
        #                 tileset,
        #             )
        #             sys.exit(1)

    def update(self) -> None:
        """Update the map object."""
        # @todo: Exctract only visible image (screen rect) from image
        # instead of moving the whole big map image.
        self.rect.x, self.rect.y = self.camera.get_relative_position(self.x, self.y)

    def get_tileset(self, tile_id: int) -> Tileset:
        """Identify the tileset based on the tile id specified in the map file."""
        for _, tileset in self.tilesets.items():
            if tile_id >= tileset.first_gid and tile_id <= tileset.last_gid:
                return tileset

        return None
