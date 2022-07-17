#!/usr/bin/env python
# coding=utf-8
import pygame as pg
import pytiled_parser as pytiled

from pysurvive.config import COLORKEY, ROOT_PATH
from pysurvive.logger import logger
from pysurvive.utils import load_image


class TilesetMapping:

    """
    Class which takes over the mapping of the individual tiles
    from the level/map config to the corresponding tiles in the
    tileset (x, y).
    """

    default = 7
    mapping = {}

    @classmethod
    def get_tile(cls, tile_id: int) -> tuple[int, int]:
        try:
            return cls.mapping[tile_id]
        except KeyError:
            return cls.mapping[cls.default]  # Default


class GroundMapping(TilesetMapping):

    """For all ground and water tilesets."""

    default = 7
    mapping = {
        1: (0, 0),  # top left
        2: (1, 0),  # top
        3: (2, 0),  # top right
        6: (0, 1),  # left
        7: (1, 1),  # middle
        8: (2, 1),  # right
        11: (0, 2),  # bottom right
        12: (1, 2),  # bottom
        13: (2, 2),  # bottom left
        9: (3, 1),  # inner top left
        10: (4, 1),  # inner top right
        4: (3, 0),  # inner bottom left
        5: (4, 0),  # inner bottom right
        # (3, 2) and (4, 2) are unset!
    }


class WallMapping(TilesetMapping):

    """Same as the ground mapping, but the middle tile is none."""

    default = 2
    mapping = {
        1: (0, 0),  # top left
        2: (1, 0),  # top
        3: (2, 0),  # top right
        6: (0, 1),  # left
        # (1, 1) is unset!
        8: (2, 1),  # right
        11: (0, 2),  # bottom right
        12: (1, 2),  # bottom
        13: (2, 2),  # bottom left
        9: (3, 1),  # inner top left
        10: (4, 1),  # inner top right
        4: (3, 0),  # inner bottom left
        5: (4, 0),  # inner bottom right
        19: (3, 3),  # outer top left
        20: (4, 3),  # outer top right
        14: (3, 2),  # outer bottom left
        15: (4, 2),  # outer bottom right
    }


class FloorMapping(TilesetMapping):

    """Floor tileset consist of only one tile."""

    default = 1
    mapping = {
        1: (0, 0),
    }


class Tileset:

    """Represents and load a tileset from filesystem."""

    def __init__(self, _config: pytiled.tileset.Tileset) -> None:
        self.config = _config
        # Single tile images in a 2d-table.
        self.table = self._load(self.image_path)
        # Contains the images of the details for the tileset.
        # self.detail_images = self._load_details(f"{self.root_path}/details")

    def __repr__(self) -> str:
        return (
            f"Tileset (name={self.name},"
            f" filename={self.filename},"
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
        except KeyError:
            return None

    @property
    def image_path(self) -> str:
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

    def get_tile(self, tile_id: int) -> tuple[int, int]:
        """Returns the tile based in the tileset type/model."""
        _tile_id = tile_id - self.first_gid + 1
        if self.model == "ground":
            return GroundMapping.get_tile(_tile_id)
        elif self.model == "wall":
            return WallMapping.get_tile(_tile_id)
        elif self.model == "floor":
            return FloorMapping.get_tile(_tile_id)
        else:
            logger.error("Invalid tileset type.")
            return None

    def _load(self, filename: str) -> list[list[pg.Rect]]:
        """Load a tileset from filename and split it into a table."""
        logger.info("Loading tileset from file %s.", filename)
        image, _ = load_image(filename, alpha=True)
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width // self.tile_width):
            line: list[pg.Surface] = []
            tile_table.append(line)
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
                    line.append(None)
                else:
                    line.append(tile_image)

        return tile_table

    # def _load_details(
    #     self, details_path: str, detail_types: tuple = ("cracks", "objects")
    # ) -> list[pg.Surface]:
    #     """Load the details images of the tileset."""
    #     object_images = []
    #     # Looking for details in directories "cracks" and "objects" and
    #     # for different image sizes.
    #     for detail in detail_types:
    #         for size in ("16", "32", "64", "128", "256", "512", "1024"):
    #             directory = f"{details_path}/{detail}/{size}"
    #             if not os.path.isdir(directory):
    #                 logger.warning("Directory %s doesnt exists.", directory)
    #                 continue
    #
    #             logger.info("Loading images from path %s.", directory)
    #             path, _, files = next(os.walk(directory))
    #             for img in sorted(files):
    #                 image, _ = load_image(f"{path}/{img}", alpha=True)
    #                 object_images.append(image)
    #
    #     return object_images
