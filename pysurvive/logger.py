#!/usr/bin/env python
# coding=utf-8
import logging
import sys

from pysurvive.config import DEBUG_LOG


class Logger:

    _logger = None

    def __new__(cls, *args, **kwargs):
        if cls._logger is None:
            cls._logger = super().__new__(cls, *args, **kwargs)
            cls._logger = logging.getLogger(__name__)
            cls._logger.setLevel(logging.DEBUG if DEBUG_LOG else logging.INFO)

            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

            cls._logger.addHandler(handler)

        return cls._logger
