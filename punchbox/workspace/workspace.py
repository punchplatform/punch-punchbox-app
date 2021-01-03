#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os

from pathlib import Path
from typing import Union

import click
import yaml

from typing_extensions import Final

from punchbox.common_lib.command_meta.command_option import CommandOption
from punchbox.common_lib.command_meta.commands import Commands
from punchbox.common_lib.data_classes import punchbox_configuration
from punchbox.common_lib.data_classes.source_hierarchy import SourceHierarchy
from punchbox.common_lib.data_classes.workspace_configuration import (
    WorkspaceConfiguration,
)
from punchbox.common_lib.data_classes.workspace_hierarchy import WorkspaceHierarchy
from punchbox.common_lib.runtime_meta import environment
from punchbox.generate.generate import generate_blueprint
from punchbox.generate.generate import generate_deployment
from punchbox.generate.generate import generate_vagrantfile
from punchbox.punch_entry_point import cli_configuration
from punchbox.punch_entry_point.cli_configuration import PunchLogger
from punchbox.utils.file import File
from punchbox.workspace import workspace_helper


@click.group(**cli_configuration.CliConfiguration.click_command_settings())
def workspace() -> None:
    """
    Setup your workspace.

    This method will create a so-called workspace folder. The workspace
    is a separate folder that will contain all your configuration files,
    and from where you will be able to start your VMs, deploy your punch,
    define your punch tenants and channels.

    The workspace is kept separated from your punchbox and punch deployer
    folders for both simplicity and maintainability.

    The default workspace is ~/punchbox-workspace.

    \f
    """
    ...


@workspace.command(name=Commands.CREATE_CMD)
@click.option(
    CommandOption.DEPLOYER_OPT,
    required=True,
    type=click.Path(exists=True),
    help="path to the punch deployer folder",
)
@click.option(
    CommandOption.WORKSPACE_OPT,
    required=False,
    default=f"{str(Path.home())}/punchbox-workspace",
    type=click.Path(),
    help="the punchbox workspace",
)
@click.option(
    CommandOption.PROFILE_OPT,
    required=False,
    default="standalone",
    type=click.Path(),
    help="the target platform topology  profile. Two profiles are supported right now, 'standalone' and"
    "'sample'. By default the standalone is picked.",
)
def create_workspace(
    deployer: Union[str, bytes, os.PathLike],
    workspace: Union[str, bytes, os.PathLike],
    profile: Union[str, bytes, os.PathLike],
) -> None:
    """
    Create a punchbox working space.

    This method will create the punchbox workspace folder. That
    folder will contain all your configuration files.
    From there you will be able to start your VMs, deploy your punch,
    define your punch tenants and channels etc..

    The workspace is kept separated from your punchbox and punch deployer
    folders because it is both simpler and easier for you to maintain
    your configurations safe.

    Should your work with a long-lived workspace we strongly suggest you use git to keep
    track of the changes.
    """
    workspace_hierarchy: WorkspaceHierarchy = WorkspaceHierarchy(str(workspace))
    pb_dir: Final[str] = environment.Environment.punchbox_install_dir()
    source_hierarchy: SourceHierarchy = SourceHierarchy(
        source_settings_dir=pb_dir, profile=str(profile)
    )
    if not os.path.exists(
        workspace_hierarchy.target_workspace_yml_file
    ) or click.confirm("Overwrite your configurations ?"):
        workspace_helper.WorkspaceHelper.create_workspace_hierarchy(workspace_hierarchy)
        workspace_helper.WorkspaceHelper.duplicate_required_files(
            source_hierarchy, workspace_hierarchy
        )
        workspace_activate_file = os.path.abspath(workspace_hierarchy.activate_sh_file)
        stdout_result: str = File.remove_file_if_exist(workspace_activate_file)
        PunchLogger().info_green(stdout_result)

        # populate the user workspace with the required starting configuration files.
        workspace_helper.WorkspaceHelper.apply_templating_required_files(
            source_hierarchy, workspace_hierarchy
        )

        # and finally create the activate.sh file
        File.write_unicode_as_text_file(
            workspace_activate_file,
            f"export PATH={os.path.abspath(str(deployer))}/bin:$PATH \n"
            f"export PUNCHPLATFORM_CONF_DIR={workspace_hierarchy.pp_conf_dir} \n",
        )

        # All done, generate the main punchbox yaml file. That file will be used
        # for all the subsequent build phases.
        workspace_config: WorkspaceConfiguration = WorkspaceConfiguration(
            profile=str(profile)
        )

        punchbox: punchbox_configuration.PunchboxConfiguration = punchbox_configuration.PunchboxConfiguration(
            workspace_hierarchy, workspace_config.workspace_type, str(deployer)
        )
        File.write_dict_as_yaml(
            workspace_hierarchy.target_workspace_yml_file,
            punchbox.punchbox_configuration_dict,
        )
        PunchLogger().info_green(f"Workspace created")


@workspace.command(name=Commands.BUILD_CMD)
@click.option(
    CommandOption.WORKSPACE_OPT,
    required=False,
    default=f"{str(Path.home())}/punchbox-workspace",
    type=click.Path(),
    help="the punchbox workspace",
)
@click.option(*CommandOption.YES_OPT, is_flag=True, default=True, help="confirmed mode")
@click.pass_context
def build_workspace(ctx, workspace: Union[str, bytes, os.PathLike], yes: bool) -> None:
    """
    Build your workspace.

    Once created, a few configuration files must be generated from
    various templates. This command make your workspace ready to move
    on to deploying a punch.

    By default this command is interactive and prompt before generating a file.
    If you want it to be silent use the confirmed mode.
    """
    conf: punchbox_configuration.Punchbox = File.read_punchbox_settings_file(
        f"{str(workspace)}/conf/punchbox/punchbox.yml"
    )

    with open(conf.punch.user_settings, "rb") as user_settings:
        user_settings_dict = yaml.load(user_settings.read(), Loader=yaml.SafeLoader)
        if "vagrant" in user_settings_dict:
            if not yes or click.confirm(
                f"generate vagrantfile {conf.vagrant.vagrantfile} ?"
            ):
                with open(conf.punch.user_topology, "rb") as topology, open(
                    conf.punch.user_settings, "rb"
                ) as settings, open(conf.vagrant.vagrantfile, "wb+") as vagrantfile:
                    PunchLogger().info_green(
                        f"  Punchbox generate vagrantfile \n"
                        f"    --settings {conf.punch.user_settings}  \n"
                        f"    --topology {conf.punch.user_topology} \n"
                        f"    --template {conf.vagrant.template} \n"
                        f"    --output {conf.vagrant.vagrantfile} \n"
                    )
                    ctx.invoke(
                        generate_vagrantfile,
                        settings=settings,
                        topology=topology,
                        template=conf.vagrant.template,
                        output=vagrantfile,
                    )

    if not yes or click.confirm(
        f"generate platform blueprint {conf.punch.blueprint} ?"
    ):
        with open(conf.punch.user_topology, "rb") as topology, open(
            conf.punch.blueprint, "wb+"
        ) as output, open(conf.punch.user_settings, "rb") as settings:
            PunchLogger().info_green(
                f"  punchbox generate blueprint \n"
                f"    --deployer {conf.env.deployer} \n"
                f"    --topology {conf.punch.user_topology} \n"
                f"    --settings {conf.punch.user_settings} \n"
                f"    --output {conf.punch.blueprint} \n"
            )
            ctx.invoke(
                generate_blueprint,
                deployer=conf.env.deployer,
                topology=topology,
                settings=settings,
                output=output,
            )

    if not yes or click.confirm(
        f"generate deployment settings {conf.punch.deployment_settings} ?"
    ):
        with open(conf.punch.blueprint, "rb") as blueprint, open(
            conf.punch.deployment_settings, "wb+"
        ) as output:
            PunchLogger().info_green(
                f"  punchbox generate deployment-settings \n"
                f"    --blueprint {conf.punch.blueprint} \n"
                f"    --template {conf.punch.deployment_settings_template} \n"
                f"    --output {conf.punch.deployment_settings} \n"
            )
            ctx.invoke(
                generate_deployment,
                blueprint=blueprint,
                template=conf.punch.deployment_settings_template,
                output=output,
            )

        with open(conf.punch.deployment_settings, "rb") as yaml_in, open(
            conf.punch.punchplatform_deployment_settings, "w+"
        ) as json_out:
            PunchLogger().info_green(
                f"  backward compatibility generation : \n"
                f"             convert \n"
                f"{conf.punch.deployment_settings} \n"
                f"             into \n"
                f"{conf.punch.punchplatform_deployment_settings} \n"
            )
            yaml_object = yaml.load(yaml_in, Loader=yaml.SafeLoader)
            json.dump(yaml_object, json_out)
