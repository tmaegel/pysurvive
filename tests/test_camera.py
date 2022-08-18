#!/usr/bin/env python
# coding=utf-8
import pytest

from pysurvive.game.core import Camera


class TestCamera:
    @pytest.fixture()
    def singleton(self):
        def _wrapper(x: int = 0, y: int = 0):
            return Camera(x, y)

        return _wrapper

    @pytest.fixture()
    def delete(self, singleton):
        def _wrapper() -> None:
            singleton().delete()

        return _wrapper

    def test_camera__singleton_without_args(self, singleton, delete):
        """Test the camera singleton."""
        camera_1 = singleton()
        camera_2 = singleton()
        assert id(camera_1) == id(camera_2)
        delete()

    def test_camera__singleton_with_args_1(self, singleton, delete):
        """Test the camera singleton with arguments."""
        camera_1 = singleton(500, 300)
        camera_2 = singleton(100, 200)
        assert id(camera_1) == id(camera_2)
        assert camera_1.position_center == (500, 300)
        assert camera_2.position_center == (500, 300)
        delete()

    def test_camera__singleton_with_args_2(self, singleton, delete):
        """Test the camera singleton with arguments."""
        camera_1 = singleton(500, 300)
        camera_2 = singleton()
        assert id(camera_1) == id(camera_2)
        assert camera_1.position_center == (500, 300)
        assert camera_2.position_center == (500, 300)
        delete()
