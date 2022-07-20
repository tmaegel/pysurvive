#!/usr/bin/env python
# coding=utf-8
import pygame as pg

from pysurvive.class_toolchain import Screen
from pysurvive.config import SCREEN_RECT


class TestScreen:
    def test_screen__singleton(self):
        """Test the screen singleton."""
        screen_1 = Screen()
        screen_2 = Screen()
        assert id(screen_1) == id(screen_2)

    def test_screen__without_args(self):
        """Test the screen class without args."""
        screen = Screen()
        assert screen.width == SCREEN_RECT.width
        assert screen.height == SCREEN_RECT.height
        assert screen.size == SCREEN_RECT.size

    def test_screen__with_args(self):
        """Test the screen class with args."""
        rect = pg.Rect(0, 0, 10, 10)
        screen = Screen(rect)
        assert screen.width == rect.width
        assert screen.height == rect.height
        assert screen.size == rect.size
