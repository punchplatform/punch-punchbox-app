#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import logging

from typing import Any
from typing import Dict
from typing import Type

from click_help_colors import HelpColorsGroup
from rich.logging import RichHandler


@dataclasses.dataclass()
class ClickSettings(object):

    cls: Type[HelpColorsGroup]
    help_headers_color: str
    help_options_color: str


class CliConfiguration(object):
    """
    static class grouping all essential configuration settings
    """

    def __init__(self) -> None:
        ...

    @staticmethod
    def click_command_settings() -> Dict[str, Any]:
        return dataclasses.asdict(
            ClickSettings(
                cls=HelpColorsGroup,
                help_headers_color="blue",
                help_options_color="green",
            )
        )


class PunchLogger(object):

    __log: logging.Logger

    def __init__(self) -> None:
        # noinspection PyArgumentList
        logging.basicConfig(
            level="NOTSET",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True)],
        )
        self.__log = logging.getLogger("punchbox")

    @property
    def logger(self) -> logging.Logger:
        return self.__log
