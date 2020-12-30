#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from pathlib import Path
from click_help_colors import HelpColorsGroup


class PunchBoxCli(object):
    """Abstract class that other cli module should inherit
    """

    @staticmethod
    @click.group(
        cls=HelpColorsGroup, help_headers_color="blue", help_options_color="green"
    )
    def cli() -> None:
        """Welcome to punchbox. This punch tool is your easy way to deploy, test or develop on
        top of the punch.

        To activate auto completion, use:

            eval "$(_PUNCHBOX_COMPLETE=source punchbox)"

        Two set of commands are available. The one under 'workspace' are the ones you are most likely
        to use. They let you build a workspace folder to configure what you need and deploy your punch.

        The ones under 'generate' are finer grain commands to selectively generate some of
        the configuration files.

        A good starting point is to type 'punchbox workspace create'
        \f
        """
        pass
