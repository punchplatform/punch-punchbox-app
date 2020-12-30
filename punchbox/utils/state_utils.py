#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing_extensions import Final


class StateCode(object):

    SUCCESS: Final[int] = 0
    FAILURE: Final[int] = 1
    UNKNOWN: Final[int] = -1
