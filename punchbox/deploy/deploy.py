#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from pathlib import Path
from typing import Union

import click

from punchbox.common_lib.command_meta.command_option import CommandOption
from punchbox.common_lib.command_meta.commands import Commands
from punchbox.common_lib.data_classes.punchbox_configuration import Punchbox
from punchbox.common_lib.runtime_meta import state_code
from punchbox.punch_entry_point import cli_configuration
from punchbox.punch_entry_point.cli_configuration import PunchLogger
from punchbox.utils.punch_file_utils import PunchFileUtils


@click.group(**cli_configuration.CliConfiguration.click_command_settings())
def deploy() -> None:
    """Commands required to deploy your punch.
    """
    ...


@deploy.command(name=Commands.AUDIT_CMD)
@click.option(
    CommandOption.WORKSPACE_OPT,
    required=False,
    default=str(Path.home()) + "/punchbox-workspace",
    type=click.Path(),
    help="the punchbox workspace",
)
@click.option(
    *CommandOption.VERBOSE_OPT, is_flag=True, default=False, help="verbose mode"
)
@click.pass_context
def deploy_audit(ctx, workspace: Union[str, bytes, os.PathLike], verbose: bool) -> int:
    """
    Audit your configuration before going any further.
    """
    conf: Punchbox = PunchFileUtils.read_punchbox_settings_file(
        f"{str(workspace)}/conf/punchbox/punchbox.yml"
    )

    audit_cmd = f"{conf.env.deployer}/bin/configuration_audit/audit3.py"
    audit_yml = (
        f"{conf.env.deployer}/bin/configuration_audit/punchplatform_dependencies.yml"
    )
    conf_file = conf.punch.deployment_settings
    if verbose:
        PunchLogger().debug_yellow(
            f"audit command: \n" f" {audit_cmd} {audit_yml} {conf_file} \n"
        )
    if state_code.StateCode.SUCCESS == os.system(
        f" {audit_cmd} {audit_yml} {conf_file}"
    ):
        PunchLogger().info_green(
            f"INFO: your generated settings {conf_file} are correct \n"
        )
        return state_code.StateCode.SUCCESS
    PunchLogger().error_red(f"ERROR: your generated settings {conf_file} are incorrect")
    return state_code.StateCode.FAILURE
