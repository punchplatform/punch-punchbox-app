#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import getpass
import grp
import logging
import os
import pwd
import sys

from typing import IO
from typing import Union

import click
import yaml

from punchbox.common_lib.command_meta.command_option import CommandOption
from punchbox.common_lib.command_meta.commands import Commands
from punchbox.generate import generate_helper
from punchbox.punch_entry_point import cli_configuration
from punchbox.punch_entry_point.cli_configuration import PunchLogger
from punchbox.utils import ansible


@click.group(**cli_configuration.CliConfiguration.click_command_settings())
def generate() -> None:
    """
    Generate deployment files.

    The generate commands lets you generate some of the configuration files you
    will need to deploy a punch. Prefer using the play commands that
    do all that for you.

    The generate commands are used to finley control each intermediate
    configuration file generation.
    \f
    """
    ...


@generate.command(name=Commands.BLUEPRINT_CMD)
@click.option(
    CommandOption.DEPLOYER_OPT,
    required=True,
    type=click.Path(exists=True),
    help="path to the punch deployer folder",
)
@click.option(
    CommandOption.TOPOLOGY_OPT,
    required=True,
    type=click.File("rb"),
    help="a punch topology description file",
)
@click.option(
    CommandOption.SETTINGS_OPT,
    required=True,
    type=click.File("rb"),
    help="the punch settings file. It provides all the required settings "
    "for the platform and each service you selected. For the standalone use the "
    "samples/standalone/settings.yml file.",
)
@click.option(
    CommandOption.OUTPUT_OPT,
    default=None,
    type=click.File("wb"),
    help="the generated platform inventory topology. "
    "If not provided the file is written to stdout",
)
def generate_blueprint(
    deployer: Union[str, bytes, os.PathLike],
    topology: IO[bytes],
    settings: IO[bytes],
    output: IO[bytes],
) -> None:
    """
        Generate the punch blueprint configuration file. That file is the one used
        to in turn generate deployment and resolver files using templates.

        It fully summarizes the information you provided through the topology
        and the settings files.

        You should not need to understand it, and certainly not to edit it as it is generated.
        It can be useful to debug a deployment issue.
    """
    settings_dict = yaml.load(settings.read(), Loader=yaml.SafeLoader)
    topology_dict = yaml.load(topology.read(), Loader=yaml.SafeLoader)
    # create a fresh new blueprint
    blueprint = {"services": {}, "platform": copy.deepcopy(settings_dict["platform"])}
    # first pass to fill all the settings
    generate_helper.compute_blueprint_setting(blueprint, settings_dict, topology_dict)
    # second pass to take care of users
    generate_helper.compute_blueprint_users(blueprint, topology_dict)
    # last path to add versions wherever needed
    generate_helper.compute_blueprint_versions(blueprint, str(deployer))
    formatted_model = yaml.dump(blueprint)
    userid = getpass.getuser()
    groupid = pwd.getpwnam(userid).pw_gid
    groupname = grp.getgrgid(groupid).gr_name
    formatted_model = formatted_model.replace("localusername", userid)
    formatted_model = formatted_model.replace("localusergroup", groupname)
    if output is None:
        PunchLogger().logger.info(formatted_model)
    else:
        output.write(formatted_model.encode(encoding="UTF-8"))


@generate.command(name=Commands.DEPLOYMENT_SETTINGS_CMD)
@click.option(
    CommandOption.BLUEPRINT_OPT,
    required=True,
    type=click.File("rb"),
    help="the platform blueprint file generated using the 'generate blueprint' command",
)
@click.option(
    CommandOption.TEMPLATE_OPT,
    required=False,
    type=click.Path(exists=True),
    help="the deployment template. The default is  "
    "templates/punchplatform_deployment_settings.j2 in your punchbox. It provides all the required "
    "settings ",
)
@click.option(CommandOption.OUTPUT_OPT, type=click.File("wb"), help="Output file")
def generate_deployment(
    blueprint: IO[bytes], template: Union[str, bytes, os.PathLike], output: IO[bytes]
) -> None:
    """
        Generate the punch deployment settings file. That file is your input to use the punch
        deployer. It contains the complete and precise settings of all your components.

        That file is, of course, a rich file. Each section of it is fully described in the punch
        online documentation. It is generated from a ready to use template file and the topology
        file generated using the 'generate topology' command.

        Once you have that file you are good to go to deploy your punch.
    """
    blueprint_dict = yaml.load(blueprint.read(), Loader=yaml.SafeLoader)
    deployment_template = ansible.load_template(template)
    try:
        output_yml = deployment_template.render(**blueprint_dict)
        if output is not None:
            output.write(output_yml.encode(encoding="UTF-8"))
        else:
            click.echo(output_yml)
    except TypeError:
        logging.exception(
            "your punchplatform-deployment-settings.j2.yaml template must be wrong"
        )
        sys.exit(1)


@generate.command(name=Commands.RESOLVER_CMD)
@click.option(
    CommandOption.BLUEPRINT_OPT,
    required=True,
    type=click.File("rb"),
    help="the platform blueprint file generated using the 'generate blueprint' command",
)
@click.option(
    CommandOption.TEMPLATE_OPT,
    required=True,
    type=click.Path(exists=True),
    help="the resolver template. In doubt use the  "
    "templates/resolv.hjson.j2 in your punchbox.",
)
@click.option(CommandOption.OUTPUT_OPT, type=click.File("wb"), help="Output file")
def generate_resolver(
    blueprint: IO[bytes], template: Union[str, bytes, os.PathLike], output: IO[bytes]
) -> None:
    """
        Generate the punch deployment resolver file. That file is required to
        deploy the punch but can be empty.
    """
    blueprint_dict = yaml.load(blueprint.read(), Loader=yaml.SafeLoader)
    deployment_template = ansible.load_template(template)
    try:
        output_yml = deployment_template.render(**blueprint_dict)
        if output is not None:
            output.write(output_yml.encode(encoding="UTF-8"))
        else:
            PunchLogger().logger.info(output_yml)
    except TypeError:
        PunchLogger().logger.exception(
            "your resolv_hjson.j2.yaml template must be wrong"
        )
        sys.exit(1)


@generate.command(name=Commands.VAGRANTFILE_CMD)
@click.option(
    CommandOption.SETTINGS_OPT,
    required=True,
    type=click.File("rb"),
    help="a punch settings configuration file",
)
@click.option(
    CommandOption.TOPOLOGY_OPT,
    required=True,
    type=click.File("rb"),
    help="a punch topology configuration file",
)
@click.option(
    CommandOption.TEMPLATE_OPT,
    required=False,
    type=click.Path(exists=True),
    help="a vagrant template file",
)
@click.option(
    CommandOption.OUTPUT_OPT,
    type=click.File("wb"),
    help="the output file where to write the Vagrant file. If not provided the generated file"
    " is written to stdout",
)
def generate_vagrantfile(
    topology: IO[bytes],
    settings: IO[bytes],
    template: Union[str, bytes, os.PathLike],
    output: IO[bytes],
) -> None:
    """
    Generate Vagrantfile.

    This command lets you easily generate a Vagrantfile from the punchbox provided
    template. You can use you own template in case you have one.

    The default template is located in the punchbox vagrant/Vagrantfile.j2 file.
    """
    if template is None:
        punchbox_dir = os.environ.get("PUNCHBOX_DIR")
        if punchbox_dir is None:
            click.echo(
                "if you do not provide a vagrant template file you must set the PUNCHBOX_DIR environment variable"
            )
            sys.exit(1)
        template = f"{punchbox_dir}/vagrant/Vagrantfile.j2"
        click.echo(f"using default vagrant template {template}")

    template_jinja = ansible.load_template(template)
    settings_dict = yaml.load(settings.read(), Loader=yaml.SafeLoader)["vagrant"]
    topology_dict = yaml.load(topology.read(), Loader=yaml.SafeLoader)
    rendered_template = template_jinja.render(**settings_dict, **topology_dict)
    if output is not None:
        output.write(rendered_template.encode(encoding="UTF-8"))
    else:
        click.echo(rendered_template)
