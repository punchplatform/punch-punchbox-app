#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import ClassVar


class StateCode(object):

    SUCCESS: ClassVar[int] = 0
    FAILURE: ClassVar[int] = 1
    UNKNOWN: ClassVar[int] = -1
