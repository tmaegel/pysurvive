#!/usr/bin/env python
# coding=utf-8
import pytest

from pysurvive.map.tileset import Tileset


class TestTileset:
    @pytest.mark.parametrize(
        "tileset, expected",
        [
            ("tests/testdata/test_tileset_2x1.png", [[1, 0]]),
            ("tests/testdata/test_tileset_2x2.png", [[0, 1], [1, 1]]),
            ("tests/testdata/test_tileset_2x3.png", [[1, 1], [1, 0], [1, 1]]),
        ],
    )
    def test_load__tile_with_colorkey_is_none(self, setup_pygame, tileset, expected):
        """Tiles with the color of the colorkey shoudl be None."""
        tileset = Tileset("test", tileset)
        print(expected)
        print(tileset.table)
        for y, row in enumerate(expected):
            for x, entry in enumerate(row):
                if entry == 0:
                    assert tileset.table[x][y] is None
                elif entry == 1:
                    assert tileset.table[x][y] is not None
