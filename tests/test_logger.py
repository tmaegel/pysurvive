#!/usr/bin/env python
# coding=utf-8
from pysurvive.logger import Logger


class TestLogger:
    def test_logger__singleton(self):
        """Test the logger singleton."""
        logger_1 = Logger()
        logger_2 = Logger()
        assert id(logger_1) == id(logger_2)
