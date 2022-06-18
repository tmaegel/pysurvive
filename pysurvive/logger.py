#!/usr/bin/env python
# coding=utf-8
import logging
import sys

from pysurvive.config import DEBUG_LOG

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if DEBUG_LOG else logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logger.addHandler(handler)
