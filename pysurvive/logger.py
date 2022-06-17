#!/usr/bin/env python
# coding=utf-8
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(name)10s - %(levelname)8s - %(message)s"))
logger.addHandler(handler)
