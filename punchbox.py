# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import click
from click_help_colors import HelpColorsGroup

from deploy.deploy_commands import deploy
from generate.generate import generate
from workspace.workspace_commands import workspace


@click.group(cls=HelpColorsGroup, help_headers_color="blue", help_options_color="green")
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


if __name__ == '__main__':
    cli.add_command(workspace)
    cli.add_command(generate)
    cli.add_command(deploy)
    cli()
