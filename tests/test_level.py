#!/usr/bin/env python
# coding=utf-8
import pytest

from pysurvive.map.level import Level


class TestLevel:
    @pytest.mark.parametrize(
        "map_file, expected",
        [
            ("tests/testdata/valid_layers_01.map", {0: ["00", ".."], 1: ["..", "00"]}),
            (
                "tests/testdata/valid_layers_02.map",
                {99: ["00", ".."], 100: ["..", "00"]},
            ),
            (
                "tests/testdata/invalid_layers_01.map",
                {},
            ),
            (
                "tests/testdata/file_not_found.map",
                {},
            ),
        ],
    )
    def test_load__valid_layers(self, setup_pygame, map_file, expected):
        """Check for valid layer parsing."""
        level = Level(self, map_file)
        assert level.map_layer_raw == expected
