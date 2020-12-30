#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
from pathlib import Path
from click_help_colors import HelpColorsGroup


@click.group(cls=HelpColorsGroup, help_headers_color="blue", help_options_color="green")
def deploy() -> None:
    """Commands required to deploy your punch.
    """
    pass


@deploy.command(name="audit")
@click.option(
    "--workspace",
    required=False,
    default=str(Path.home()) + "/punchbox-workspace",
    type=click.Path(),
    help="the punchbox workspace",
)
@click.option("--verbose", "-v", is_flag=True, default=False, help="verbose mode")
@click.pass_context
def deploy_audit(ctx, workspace, verbose):
    """
    Audit your configuration before going any further.
    """
    with open(workspace + "/conf/punchbox/punchbox.yml") as infile:
        conf = yaml.load(infile.read(), Loader=yaml.SafeLoader)
    audit_cmd = conf["env"]["deployer"] + "/bin/configuration_audit/audit3.py"
    audit_yml = (
        conf["env"]["deployer"]
        + "/bin/configuration_audit/punchplatform_dependencies.yml"
    )
    conf_file = conf["punch"]["deployment_settings"]
    if verbose:
        print("audit command:")
        print(" " + audit_cmd + " " + audit_yml + " " + conf_file)
    if 0 == os.system(audit_cmd + " " + audit_yml + " " + conf_file):
        print("INFO: your generated settings " + conf_file + " are correct")
        return 0
    print("ERROR: your generated settings " + conf_file + " are incorrect")
    return 1
