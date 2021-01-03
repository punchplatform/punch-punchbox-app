#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import ClassVar


class Key(object):

    VAGRANT: ClassVar[str] = "vagrant"
    PUNCH: ClassVar[str] = "punch"
    ENV: ClassVar[str] = "env"
    VERSION: ClassVar[str] = "version"
    PUNCH_LOGGER: ClassVar[str] = "punch_logger"
