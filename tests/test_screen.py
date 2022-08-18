#!/usr/bin/env python
# coding=utf-8
import pygame as pg
import pytest

from pysurvive.config import SCREEN_RECT
from pysurvive.game.core import Screen


class TestScreen:
    @pytest.fixture()
    def singleton(self):
        def _wrapper(rect: pg.Rect = None):
            return Screen(rect)

        return _wrapper

    @pytest.fixture()
    def delete(self, singleton):
        def _wrapper() -> None:
            singleton().delete()

        return _wrapper

    def test_screen__singleton_without_args(self, singleton, delete):
        """Test the screen singleton without arguments."""
        screen_1 = singleton()
        screen_2 = singleton()
        assert id(screen_1) == id(screen_2)
        assert screen_1.width == SCREEN_RECT.width
        assert screen_1.height == SCREEN_RECT.height
        assert screen_1.size == SCREEN_RECT.size
        assert screen_2.width == SCREEN_RECT.width
        assert screen_2.height == SCREEN_RECT.height
        assert screen_2.size == SCREEN_RECT.size
        delete()

    def test_screen__singleton_with_args_1(self, singleton, delete):
        """Test the screen singleton with args."""
        rect_1 = pg.Rect(0, 0, 10, 10)
        screen_1 = singleton(rect_1)
        screen_2 = singleton()
        assert id(screen_1) == id(screen_2)
        assert screen_1.width == rect_1.width
        assert screen_1.height == rect_1.height
        assert screen_1.size == rect_1.size
        assert screen_2.width == rect_1.width
        assert screen_2.height == rect_1.height
        assert screen_2.size == rect_1.size
        delete()

    def test_screen__singleton_with_args_2(self, singleton, delete):
        """Test the screen singleton with args."""
        rect_1 = pg.Rect(0, 0, 10, 10)
        rect_2 = pg.Rect(0, 0, 60, 60)
        screen_1 = singleton(rect_1)
        screen_2 = singleton(rect_2)
        assert id(screen_1) == id(screen_2)
        assert screen_1.width == rect_1.width
        assert screen_1.height == rect_1.height
        assert screen_1.size == rect_1.size
        assert screen_2.width == rect_1.width
        assert screen_2.height == rect_1.height
        assert screen_2.size == rect_1.size
        delete()
