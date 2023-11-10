#!/usr/bin/env python
# coding=utf-8

import pygame as pg

from pysurvive.config import DEBUG_SPRITE, RED


class CameraBoxBorder:
    left: int = 300
    right: int = 300
    top: int = 300
    bottom: int = 300


class Camera(pg.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pg.display.get_surface()
        self.width = self.display_surface.get_size()[0]
        self.height = self.display_surface.get_size()[1]
        self.screenx = self.width // 2
        self.screeny = self.height // 2
        self.offset = pg.math.Vector2()

        self.camera_box = pg.Rect(
            CameraBoxBorder.left,
            CameraBoxBorder.top,
            self.width - (CameraBoxBorder.left + CameraBoxBorder.right),
            self.height - (CameraBoxBorder.top + CameraBoxBorder.bottom),
        )

    def __repr__(self) -> str:
        return f"Camera(x={self.x} x {self.x})"

    @property
    def x(self) -> float:
        return self.offset.x

    @property
    def y(self) -> float:
        return self.offset.y

    @x.setter
    def x(self, _x: float) -> None:
        self.offset.x = _x

    @y.setter
    def y(self, _y: float) -> None:
        self.offset.y = _y

    @property
    def rect(self) -> pg.FRect:
        """Returns the camera / screen rect."""
        return pg.FRect(self.x, self.y, self.width, self.height)

    @property
    def near_area_rect(self) -> pg.FRect:
        return pg.FRect(
            self.x + self.screenx - 75, self.y + self.screeny - 75, 150, 150
        )

    def update(self, target) -> None:
        if target.x < self.camera_box.left:
            self.camera_box.left = target.x
        if target.x > self.camera_box.right:
            self.camera_box.right = target.x
        if target.y < self.camera_box.top:
            self.camera_box.top = target.y
        if target.y > self.camera_box.bottom:
            self.camera_box.bottom = target.y

        self.x = self.camera_box.left - CameraBoxBorder.left
        self.y = self.camera_box.top - CameraBoxBorder.top
