#!/usr/bin/env python
# coding=utf-8
import copy
import sys
from os.path import exists as file_exists
from pathlib import Path
from typing import Optional

import pygame as pg
import pytiled_parser as pytiled

from pysurvive.game.core import Screen
from pysurvive.logger import Logger
from pysurvive.map.tileset import Tileset

logger = Logger()


class TileGroup(pg.sprite.RenderPlain):
    def __init__(self):
        super().__init__()


class Level:

    """
    Load a map file from disk and draw it on a surface.
    The level object acts wrapper around multiple groups which
    contains every tile object from the map.

    In addition, the respective tile objects are divided
    into further groups for differentiation according to
    the respective properties (block, enter, close to player).
    """

    def __init__(self, _map_file: str) -> None:
        self.screen = Screen()

        logger.info("Loading map from file %s.", _map_file)
        if not file_exists(_map_file):
            logger.error("Map file %s does not exists.", _map_file)
            sys.exit(1)

        # Load map config.
        self.map_file = Path(_map_file)
        self.map_config = pytiled.parse_map(self.map_file)

        # Load tilesets.
        self.tilesets = {}
        for ts_id, ts_config in self.map_config.tilesets.items():
            tileset = Tileset(ts_config)
            self.tilesets[ts_id] = tileset

        # The whole list of tiles in one group.
        self.tiles_all = TileGroup()
        # Tiles that should draw on the screen.
        self.tiles_screen = TileGroup()
        # Includes only objects which cannot be entered.
        self.tiles_not_enterable = TileGroup()
        # Includes only objects which do not block (e.g. shooting)
        self.tiles_blockable = TileGroup()
        # @todo
        # self.close_to_player = TileGroup()

        self._initialize()

    @property
    def map_width(self) -> float:
        """Returns the map width (tile x * tile size)."""
        return self.map_config.map_size.width * self.map_config.tile_size.width

    @property
    def map_height(self) -> float:
        """Returns the map height (tile y * tile size)."""
        return self.map_config.map_size.height * self.map_config.tile_size.height

    def _initialize(self) -> None:
        """Initialize each layer of the tile map."""
        for layer in self.map_config.layers:
            # Exlude non TileLayer layers.
            if not isinstance(layer, pytiled.layer.TileLayer):
                continue

            for y, row in enumerate(layer.data):
                for x, tile_id in enumerate(row):
                    tileset = self._get_tileset(tile_id)
                    if not tileset:
                        continue

                    tile_index = tileset.get_tile_index(tile_id)
                    try:
                        tile = copy.deepcopy(tileset.get_tile(tile_id))
                        tile.x = x * self.map_config.tile_size.width
                        tile.y = y * self.map_config.tile_size.height
                        # Add a copy of tile from tileset.
                        self.tiles_all.add((tile,))
                        if not tile.enter:
                            self.tiles_not_enterable.add((tile,))
                        if tile.block:
                            self.tiles_blockable.add((tile,))
                    except IndexError:
                        logger.error(
                            "Error while accessing tile (%s) of tileset %r.",
                            tile_index,
                            tileset,
                        )
                        sys.exit(1)

    def _get_tileset(self, tile_id: int) -> Optional[Tileset]:
        """
        Identify the tileset based on the tile id specified
        in the map file.
        """
        for _, tileset in self.tilesets.items():
            if tile_id >= tileset.first_gid and tile_id <= tileset.last_gid:
                return tileset

        return None

    def update(self, *args, **kwargs):
        """
        Call the update method of every tile object.
        Check which tile is one the screen.
        """
        self.tiles_screen.empty()
        self.tiles_screen.add(
            pg.sprite.spritecollide(self.screen, self.tiles_all, False)
        )
        # Update all tiles on the screen.
        self.tiles_all.update(*args, **kwargs)

    def draw(self, surface: pg.surface.Surface) -> None:
        """
        Draw all sprites (tiles) onto the surface
        Group.draw(surface): return Rect_list
        Draws all of the member sprites onto the given surface.
        """
        self.tiles_screen.draw(surface)
