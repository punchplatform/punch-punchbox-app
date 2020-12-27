import os
import shutil
import click
import yaml
from click_help_colors import HelpColorsGroup
from copy import deepcopy
from os.path import dirname
from pathlib import Path

from generate import generate


def copy_to_workspace(src, dst) -> None:
    """Copy a reference file to

    :param src: the src path
    :param dst: the destination path
    :return: None
    """
    if os.path.exists(os.path.abspath(dst)):
        click.echo("overwriting " + dst)
    shutil.copy(os.path.abspath(src), os.path.abspath(dst))


def create_dir_if_needed(*dirs) -> None:
    """Create a bunch of directories

    :param dirs: one or several directory paths
    :return: None
    """
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)


@click.group(cls=HelpColorsGroup, help_headers_color="blue", help_options_color="green")
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
    pass


@workspace.command(name="create")
@click.option("--deployer",
              required=True,
              type=click.Path(exists=True),
              help="path to the punch deployer folder")
@click.option("--workspace",
              required=False,
              default=str(Path.home()) + '/punchbox-workspace',
              type=click.Path(),
              help="the punchbox workspace")
@click.option("--profile",
              required=False,
              default='standalone',
              type=click.Path(),
              help="the target platform topology  profile. Two profiles are supported right now, 'standalone' and"
                   "'sample'. By default the standalone is picked."
              )
def create_workspace(deployer, workspace, profile):
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
    pb_dir = dirname(dirname(os.path.realpath(__file__)))
    workspace_top_conf_dir = workspace + "/conf"
    workspace_punchbox_conf_dir = workspace_top_conf_dir + '/punchbox'
    workspace_generated_conf_dir = workspace_punchbox_conf_dir + "/generated"
    workspace_pp_conf_dir = workspace + "/punchplatform-conf"
    workspace_vagrant_dir = workspace + "/vagrant"
    workspace_template_dir = workspace_punchbox_conf_dir + '/templates'

    src_settings = pb_dir + '/samples/' + profile + '/settings.yml'
    src_topology = pb_dir + '/samples/' + profile + '/topology.yml'
    src_resolv = pb_dir + '/samples/' + profile + '/resolv.yml'
    src_vagrant_j2 = pb_dir + '/vagrant/Vagrantfile.j2'
    dst_resolv = workspace_top_conf_dir + '/resolv.yml'
    dst_settings = workspace_top_conf_dir + '/settings.yml'
    dst_topology = workspace_top_conf_dir + '/topology.yml'
    dst_vagrant_j2 = workspace + '/vagrant/Vagrantfile.j2'

    # Generated files when executing the 'build' command
    target_vagrant_file = workspace_vagrant_dir + '/Vagrantfile'
    target_blueprint_yml = workspace_generated_conf_dir + '/blueprint.yml'
    target_workspace_yml = workspace_punchbox_conf_dir + "/punchbox.yml"
    target_deployment_settings_yml = workspace_pp_conf_dir + '/deployment-settings.yml'
    target_legacy_deployment_settings = workspace_pp_conf_dir + '/punchplatform-deployment.settings'
    target_deployment_settings_yml_j2 = workspace_template_dir + '/deployment.settings.j2'

    if not os.path.exists(target_workspace_yml) or click.confirm('Overwrite your configurations ?'):
        create_dir_if_needed(workspace_template_dir, workspace_template_dir, workspace_pp_conf_dir,
                             workspace_vagrant_dir, workspace_generated_conf_dir)
        copy_to_workspace(src_topology, dst_topology)
        copy_to_workspace(src_settings, dst_settings)
        copy_to_workspace(src_resolv, dst_resolv)
        copy_to_workspace(src_vagrant_j2, dst_vagrant_j2)

        workspace_activate_file = os.path.abspath(workspace + '/activate.sh')
        if os.path.exists(workspace_activate_file):
            print("cleaning " + workspace_activate_file)
            os.remove(workspace_activate_file)

        # populate the user workspace with the required starting configuration files.

        template_dir = os.path.abspath(pb_dir + '/templates/')
        src_files = os.listdir(template_dir)
        for file_name in src_files:
            full_file_name = os.path.join(template_dir, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, os.path.abspath(workspace_template_dir))

        # and finally create the activate.sh file
        with open(workspace_activate_file, "w+") as activateFile:
            activateFile.write("export PATH=" + os.path.abspath(deployer) + "/bin:$PATH\n")
            activateFile.write("export PUNCHPLATFORM_CONF_DIR=" + workspace_pp_conf_dir + "\n")

        # All done, generate the main punchbox yaml file. That file will be used
        # for all the subsequent build phases.
        workspace_type = 'deployed'
        if profile is 'standalone':
            workspace_type = 'standalone'

        dictionary = {
            'version': '1.0',
            'env': {
                "deployer": deployer,
                "type": workspace_type,
                "workspace": os.path.abspath(workspace),
                "vagrantfile": os.path.abspath(target_vagrant_file)
            },
            'vagrant': {
                "template": os.path.abspath(dst_vagrant_j2),
                "vagrantfile": os.path.abspath(target_vagrant_file)
            },
            'punch': {
                "blueprint": os.path.abspath(target_blueprint_yml),
                "user_topology": os.path.abspath(dst_topology),
                "user_settings": os.path.abspath(dst_settings),
                "user_resolver": os.path.abspath(dst_resolv),
                "deployment_settings_template": os.path.abspath(target_deployment_settings_yml_j2),
                "deployment_settings": os.path.abspath(target_deployment_settings_yml),
                "punchplatform_deployment_settings": os.path.abspath(target_legacy_deployment_settings),
                "resolv_conf": os.path.abspath(workspace_pp_conf_dir + '/resolv.hjson'),
                "resolv_conf_template": os.path.abspath(workspace_template_dir + '/resolv.hjson.j2')
            }
        }
        with open(target_workspace_yml, 'w+') as outfile:
            yaml.dump(dictionary, outfile)
        click.echo("workspace created")


@workspace.command(name="build")
@click.option("--workspace",
              required=False,
              default=str(Path.home()) + '/punchbox-workspace',
              type=click.Path(),
              help="the punchbox workspace")
@click.option('--yes', '-y', is_flag=True, default=True, help="confirmed mode")
@click.pass_context
def build_workspace(ctx, workspace, yes):
    """
    Build you workspace.

    Once created, a few configuration files must be generated from
    various templates. This command make your workspace ready to move
    on to deploying a punch.

    By default this command is interactive and prompt before generating a file.
    If you want it to be silent use the confirmed mode.
    """
    with open(workspace + "/conf/punchbox/punchbox.yml") as infile:
        conf = yaml.load(infile.read(), Loader=yaml.SafeLoader)

    try:
        version = conf['version']
    except KeyError:
        click.echo('invalid workspace ' + workspace)
        raise click.Abort()

    with open(conf['punch']['user_settings']) as user_settings:
        user_settings_dict = yaml.load(user_settings.read(), Loader=yaml.SafeLoader)
        if 'vagrant' in user_settings_dict:
            if not yes or click.confirm('generate vagrantfile ' + conf['vagrant']['vagrantfile'] + ' ?'):
                with open(conf['punch']['user_topology']) as topology, \
                        open(conf['punch']['user_settings']) as settings, \
                        open(conf['vagrant']['vagrantfile'], 'w+') as vagrantfile:
                    print("  punchbox generate vagrantfile \n" +
                          "    --settings " + conf['punch']['user_settings'] + "  \n" +
                          "    --topology " + conf['punch']['user_topology'] + "  \n" +
                          "    --template " + conf['vagrant']['template'] + "  \n" +
                          "    --output " + conf['vagrant']['vagrantfile'] + "\n")
                    ctx.invoke(generate.generate_vagrantfile, settings=settings, topology=topology,
                               template=conf['vagrant']['template'], output=vagrantfile)

    if not yes or click.confirm('generate platform blueprint ' + conf['punch']['blueprint'] + ' ?'):
        with open(conf['punch']['user_topology'], "r") as topology, \
                open(conf['punch']['blueprint'], "w+") as output, \
                open(conf['punch']['user_settings'], "r") as settings:
            print("  punchbox generate blueprint \n" +
                  "    --deployer " + conf['env']['deployer'] + "  \n" +
                  "    --topology " + conf['punch']['user_topology'] + "  \n" +
                  "    --settings " + conf['punch']['user_settings'] + "  \n" +
                  "    --output " + conf['punch']['blueprint'] + "\n")
            ctx.invoke(generate.generate_blueprint,
                       deployer=conf['env']['deployer'],
                       topology=topology,
                       settings=settings,
                       output=output)

    if not yes or click.confirm('generate deployment settings ' + conf['punch']['deployment_settings'] + ' ?'):
        with open(conf['punch']['blueprint'], "r") as blueprint, \
                open(conf['punch']['deployment_settings'], "w+") as output:
            print("  punchbox generate deployment-settings \\\n" +
                  "    --blueprint " + conf['punch']['blueprint'] + "  \\\n" +
                  "    --template " + conf['punch']['deployment_settings_template'] + "  \\\n" +
                  '    --output ' + conf['punch']['deployment_settings'] + "\n")
            ctx.invoke(generate.generate_deployment,
                       blueprint=blueprint,
                       template=conf['punch']['deployment_settings_template'],
                       output=output)

        with open(conf['punch']['deployment_settings'], 'r') as yaml_in, \
                open(conf['punch']['punchplatform_deployment_settings'], "w+") as json_out:
            print("  backward compatibility generation : convert\n" +
                  "    " + conf['punch']['deployment_settings'] + " into \n" +
                  "            into \n" +
                  "    " + conf['punch']['punchplatform_deployment_settings'] + "\n")
            yaml_object = yaml.load(yaml_in, Loader=yaml.SafeLoader)
            # yaml_object = yaml.safe_load(yaml_in)
            json.dump(yaml_object, json_out)
