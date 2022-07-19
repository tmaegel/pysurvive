#!/usr/bin/env python
# coding=utf-8
import pytest

from pysurvive.config import COLORKEY
from pysurvive.map.tileset import Tileset


class TestTileset:
    @pytest.mark.parametrize(
        "tileset",
        [
            ("tests/testdata/tileset/tilelist.png"),
        ],
    )
    def test_load__valid_tileset(self, setup_pygame, tileset):
        """Test if the tileset is detected and cut correctly."""
        tile_table = Tileset._load(tileset, 64, 64)
        print(tile_table)
        for tile in tile_table:
            assert tile.get_at((0, 0)) == COLORKEY
