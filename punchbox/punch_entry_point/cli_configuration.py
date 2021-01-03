#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import logging

from typing import Any
from typing import Dict
from typing import Type

from click_help_colors import HelpColorsGroup
from rich.logging import RichHandler

from punchbox.common_lib.runtime_meta.environment import Environment
from punchbox.common_lib.runtime_meta.key import Key


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

    # noinspection PyArgumentList
    logging.basicConfig(
        level=Environment.punchbox_log_level(),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    __log: logging.Logger = logging.getLogger(Key.PUNCH_LOGGER)

    @property
    def logger(self) -> logging.Logger:
        return self.__log

    def error_red(self, message: str) -> None:
        self.__log.error(msg=f"[bold red]{message}[/]", extra={"markup": True})

    def info_green(self, message: str) -> None:
        self.__log.info(msg=f"[bold green]{message}[/]", extra={"markup": True})

    def info_markup_only(self, message: str) -> None:
        self.__log.info(msg=f"{message}", extra={"markup": True})

    def debug_yellow(self, message: str) -> None:
        self.__log.debug(msg=f"[bold yellow]{message}[/]", extra={"markup": True})
