#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from punchbox.punchbox_cli import PunchBoxCli
from punchbox.deploy.deploy import deploy
from punchbox.generate.generate import generate
from punchbox.workspace.workspace import workspace
from typing import Callable


def main() -> None:
    cli: Callable = PunchBoxCli.cli

    cli.add_command(deploy)
    cli.add_command(generate)
    cli.add_command(workspace)

    cli()


if __name__ == "__main__":
    """
    This part is intended for debugging/dev mode purpose only
    """
    main()
