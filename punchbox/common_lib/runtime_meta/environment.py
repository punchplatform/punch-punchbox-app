#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from typing import ClassVar
from typing import Optional


class Environment(object):

    PUNCHPLATFORM_PUNCHBOX_INSTALL_DIR: ClassVar[
        str
    ] = "PUNCHPLATFORM_PUNCHBOX_INSTALL_DIR"

    def __init__(self) -> None:
        """
        static class
        """

    @staticmethod
    def punchbox_install_dir() -> str:
        """
        If punchbox install dir is resolved to None, set current terminal location as current directory that contains
        all your configuration files.

        Those configuration files are expected to follow a directory hierarchy:

        .. code-block:: shell

            profiles
              profile1
                resolv.yml
                settings.yml
                topology.yml
              profile2
                ...
        """
        configuration_directory: Optional[str] = os.getenv(
            Environment.PUNCHPLATFORM_PUNCHBOX_INSTALL_DIR, None
        )
        if configuration_directory is None:
            configuration_directory = os.getcwd()
        return configuration_directory
