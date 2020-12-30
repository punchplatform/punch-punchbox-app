#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

from rich.traceback import install

from punchbox.deploy import deploy
from punchbox.generate import generate
from punchbox.punch_entry_point import punchbox_cli
from punchbox.workspace import workspace


install()


def main() -> None:

    cli: Any = punchbox_cli.cli
    cli.add_command(deploy.deploy)
    cli.add_command(generate.generate)
    cli.add_command(workspace.workspace)
    cli()


if __name__ == "__main__":
    """
    This part is intended for debugging/dev mode purpose only
    """
    main()
