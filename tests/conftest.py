#!/usr/bin/env python
# coding=utf-8
import pygame as pg
import pytest


@pytest.fixture
def setup_pygame():
    pg.init()
    _ = pg.display.set_mode((800, 600), pg.HIDDEN)
