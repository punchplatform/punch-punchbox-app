import grp
import os
import pwd
from copy import deepcopy

import click
import yaml
from click_help_colors import HelpColorsGroup
import getpass
from utils.ansible_templating_utils import load_template, get_components_version
import logging


@click.group(cls=HelpColorsGroup, help_headers_color="blue", help_options_color="green")
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
    pass


def compute_blueprint_service_settings(blueprint, service_name, settings_dict, topology_dict):
    """Form a complex number.

    Keyword arguments:
        blueprint -- the blueprint to fill
        service_name -- the name of a service, i.e. kafka, shiva
        settings_dict -- the user settings dictionary. It contains platform and cluster wide settings
        topology_dict -- the user topology dictionary, It contains the servers dictionary
    """
    try:
        plf_global_settings = settings_dict['platform']
    except KeyError:
        raise click.BadParameter("missing mandatory 'platform' section in your setting file")

    if service_name not in blueprint['services']:
        blueprint['services'][service_name] = {}
        blueprint['services'][service_name]['settings'] = {}
        blueprint['services'][service_name]['clusters'] = {}
    else:
        raise click.BadParameter("duplicated service " + service_name + " in your settings")

    # this is a mere shortcut to keep the code compact
    blp_service_dict = blueprint['services'][service_name]
    try:
        plf_service_settings = settings_dict['services'][service_name]['settings']
    except KeyError:
        plf_service_settings = {}

    # Add these platform wide settings, if any, to the blueprint
    blp_service_dict['settings'] = deepcopy({**plf_service_settings, **plf_global_settings})
    # print(yaml.dump(blueprint))
    # loop over all the servers of the topology and find out where we have this
    # service
    for server_name, server_dict in topology_dict['servers'].items():
        if 'services' in server_dict:
            # print(yaml.dump(blueprint))
            for this_server_service in server_dict['services']:
                # the default cluster name is 'common'
                this_cluster_name = 'common'
                if 'cluster' in this_server_service:
                    this_cluster_name = this_server_service['cluster']

                if this_cluster_name not in blp_service_dict['clusters']:
                    # here we set the cluster section of this server.
                    blp_service_dict['clusters'][this_cluster_name] = {}
                    blp_service_dict['clusters'][this_cluster_name]['servers'] = {}
                    blp_service_dict['clusters'][this_cluster_name]['settings'] = deepcopy(plf_service_settings)
                # print(yaml.dump(blueprint))
                blp_cluster = blp_service_dict['clusters'][this_cluster_name]
                if server_name not in blp_cluster['servers']:
                    blp_cluster['servers'][server_name] = {}
                    blp_cluster['servers'][server_name]['settings'] = {}
                # print(yaml.dump(blueprint))
                try:
                    for prop_key, prop_value in \
                            settings_dict['services'][service_name]['clusters'][this_cluster_name]['settings'].items():
                        blp_cluster['settings'][prop_key] = prop_value
                except KeyError:
                    pass
                # print(yaml.dump(blueprint))
                try:
                    for prop_key, prop_value in blp_cluster['settings'].items():
                        blp_cluster['servers'][server_name]['settings'][prop_key] = prop_value
                except KeyError:
                    pass
                try:
                    for prop_key, prop_value in server_dict['settings'].items():
                        blp_cluster['servers'][server_name]['settings'][prop_key] = prop_value
                except KeyError:
                    pass
                # print(yaml.dump(blueprint))


def compute_blueprint_setting(blueprint, settings_dict, topology_dict):
    """Compute the blueprint settings at all three levels: platform, cluster and server.

    :param blueprint:  the blueprint to fill
    :param settings_dict: the user settings dictionary. It contains platform and cluster wide settings
    :param topology_dict: the user topology dictionary, It contains the servers dictionary
    :return:
    """

    if 'services' in settings_dict:
        for service_name, service_dict in settings_dict['services'].items():
            compute_blueprint_service_settings(blueprint, service_name, settings_dict, topology_dict)


def compute_blueprint_versions(blueprint, deployer_path):
    """Add the version to each service settings.

    This is only performed if the service is known to the punch deployer and if a version
    is not already specified in there.

    :param deployer_path:
    :param blueprint:
    :return:
    """
    versions_dict = get_components_version(deployer_path)
    for service_name, service in blueprint['services'].items():
        if 'version' not in service['settings']:
            if service_name in versions_dict:
                service['settings']['version'] = versions_dict[service_name]


def compute_blueprint_users(blueprint, topology_dict):
    """Compute the blueprint users.

    Keyword arguments:
        blueprint -- the blueprint to fill
        settings_dict -- the user settings dictionary. It contains platform and cluster wide settings
        topology_dict -- the user topology dictionary, It contains the servers dictionary
    """
    blueprint['users'] = {}
    if 'servers' in topology_dict:
        for host, item in topology_dict['servers'].items():
            if 'users' in item:
                for s in item["users"]:
                    settings = {}
                    user = None
                    for key, value in s.items():
                        if key == "user":
                            user = s[key]
                        elif key == "settings":
                            settings = s[key]
                        else:
                            raise click.BadParameter("only 'user' and 'settings' keys are allowed for server 'users'")
                    if user not in blueprint['users']:
                        blueprint['users'][user] = {}
                    blueprint['users'][user] = deepcopy(settings)


@generate.command(name="blueprint")
@click.option("--deployer",
              required=True,
              type=click.Path(exists=True),
              help="path to the punch deployer folder")
@click.option("--topology", required=True, type=click.File("rb"),
              help="a punch topology description file")
@click.option("--settings", required=True, type=click.File("rb"),
              help="the punch settings file. It provides all the required settings "
                   "for the platform and each service you selected. For the standalone use the "
                   "samples/standalone/settings.yml file.")
@click.option("--output", default=None, type=click.File("w"),
              help="the generated platform inventory topology. "
                   "If not provided the file is written to stdout")
def generate_blueprint(deployer, topology, settings, output):
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
    blueprint = {'services': {}, 'platform': deepcopy(settings_dict['platform'])}
    # first pass to fill all the settings
    compute_blueprint_setting(blueprint, settings_dict, topology_dict)
    # second pass to take care of users
    compute_blueprint_users(blueprint, topology_dict)
    # last path to add versions wherever needed
    compute_blueprint_versions(blueprint, deployer)
    formatted_model = yaml.dump(blueprint)
    userid = getpass.getuser()
    groupid = pwd.getpwnam(userid).pw_gid
    groupname = grp.getgrgid(groupid).gr_name
    formatted_model = formatted_model.replace('localusername', userid)
    formatted_model = formatted_model.replace('localusergroup', groupname)
    if output is None:
        print(formatted_model)
    else:
        output.write(formatted_model)


@generate.command(name="deployment-settings")
@click.option("--blueprint", required=True, type=click.File("rb"),
              help="the platform blueprint file generated using the 'generate blueprint' command")
@click.option("--template", required=False, type=click.Path(exists=True),
              help="the deployment template. The default is  "
                   "templates/punchplatform_deployment_settings.j2 in your punchbox. It provides all the required "
                   "settings ")
@click.option("--output", type=click.File("w"), help="Output file")
def generate_deployment(blueprint, template, output):
    """
        Generate the punch deployment settings file. That file is your input to use the punch
        deployer. It contains the complete and precise settings of all your components.

        That file is, of course, a rich file. Each section of it is fully described in the punch
        online documentation. It is generated from a ready to use template file and the topology
        file generated using the 'generate topology' command.

        Once you have that file you are good to go to deploy your punch.
    """
    blueprint_dict = yaml.load(blueprint.read(), Loader=yaml.SafeLoader)
    deployment_template = load_template(template)
    try:
        output_yml = deployment_template.render(**blueprint_dict)
        if output is not None:
            output.write(output_yml)
        else:
            print(output_yml)
    except TypeError:
        logging.exception("your punchplatform-deployment-settings.j2.yaml template must be wrong")
        exit(1)


@generate.command(name="resolver")
@click.option("--blueprint", required=True, type=click.File("rb"),
              help="the platform blueprint file generated using the 'generate blueprint' command")
@click.option("--template", required=True, type=click.Path(exists=True),
              help="the resolver template. In doubt use the  "
                   "templates/resolv.hjson.j2 in your punchbox.")
@click.option("--output", type=click.File("w"), help="Output file")
def generate_resolver(blueprint, template, output):
    """
        Generate the punch deployment resolver file. That file is required to
        deploy the punch but can be empty.
    """
    blueprint_dict = yaml.load(blueprint.read(), Loader=yaml.SafeLoader)
    deployment_template = load_template(template)
    try:
        output_yml = deployment_template.render(**blueprint_dict)
        if output is not None:
            output.write(output_yml)
        else:
            print(output_yml)
    except TypeError:
        click.echo("your resolv_hjson.j2.yaml template must be wrong")
        exit(1)


@generate.command(name="vagrantfile")
@click.option("--settings", required=True, type=click.File("rb"),
              help="a punch settings configuration file")
@click.option("--topology", required=True, type=click.File("rb"),
              help="a punch topology configuration file")
@click.option("--template", required=False, type=click.Path(exists=True),
              help="a vagrant template file")
@click.option("--output", type=click.File("w"),
              help="the output file where to write the Vagrant file. If not provided the generated file"
                   " is written to stdout")
def generate_vagrantfile(topology, settings, template: str, output):
    """
    Generate Vagrantfile.

    This command lets you easily generate a Vagrantfile from the punchbox provided
    template. You can use you own template in case you have one.

    The default template is located in the punchbox vagrant/Vagrantfile.j2 file.
    """
    if template is None:
        punchbox_dir = os.environ.get('PUNCHBOX_DIR')
        if punchbox_dir is None:
            click.echo(
                'if you do not provide a vagrant template file you must set the PUNCHBOX_DIR environment variable')
            exit(1)
        template = punchbox_dir + '/vagrant/Vagrantfile.j2'
        click.echo('using default vagrant template ' + template)

    template_jinja = load_template(template)
    settings_dict = yaml.load(settings.read(), Loader=yaml.SafeLoader)['vagrant']
    topology_dict = yaml.load(topology.read(), Loader=yaml.SafeLoader)
    rendered_template = template_jinja.render(**settings_dict, **topology_dict)
    if output is not None:
        output.write(rendered_template)
    else:
        print(rendered_template)
