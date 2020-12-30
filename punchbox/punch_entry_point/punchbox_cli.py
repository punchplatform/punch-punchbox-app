#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click

from punchbox.punch_entry_point import cli_configuration


@click.group(**cli_configuration.CliConfiguration.click_command_settings())
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
    ...
