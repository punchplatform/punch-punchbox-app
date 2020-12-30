#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy

from typing import Any
from typing import Dict
from typing import Optional

import click

from punchbox.utils import ansible_templating_utils


def raise_if_platform_missing_else_return(
    settings_dict: Dict[str, Any]
) -> Dict[str, str]:
    platform_dict: Optional[Dict[str, str]] = settings_dict.get("platform", None)
    if platform_dict is None:
        raise click.BadParameter(
            "missing mandatory 'platform' section in your setting file"
        )
    return platform_dict


def raise_if_duplicate_service_name_else_return(
    blueprint: Dict[str, Any], service_name: str
) -> Dict[str, Any]:
    if service_name not in blueprint["services"]:
        return {"settings": {}, "clusters": {}}
    else:
        raise click.BadParameter(f"duplicated service {service_name} in your settings")


def empty_dict_if_key_not_exist(
    settings_dict: Dict[str, Any], service_name: str
) -> Dict[str, Any]:
    try:
        return settings_dict["services"][service_name]["settings"]
    except KeyError:
        return {}


# flake8: noqa: C901
def compute_blueprint_service_settings(
    blueprint: Dict[str, Any],
    service_name: str,
    settings_dict: Dict[str, Any],
    topology_dict: Dict[str, Any],
) -> None:
    """Form a complex number.

    Keyword arguments:
        blueprint -- the blueprint to fill
        service_name -- the name of a service, i.e. kafka, shiva
        settings_dict -- the user settings dictionary. It contains platform and cluster wide settings
        topology_dict -- the user topology dictionary, It contains the servers dictionary
    """
    plf_global_settings: Dict[str, Any] = raise_if_platform_missing_else_return(
        settings_dict
    )
    blp_service_dict: Dict[str, Any] = raise_if_duplicate_service_name_else_return(
        blueprint, service_name
    )
    plf_service_settings: Dict[str, Any] = empty_dict_if_key_not_exist(
        settings_dict, service_name
    )

    # Add these platform wide settings, if any, to the blueprint
    blp_service_dict["settings"] = copy.deepcopy(
        {**plf_service_settings, **plf_global_settings}
    )
    # print(yaml.dump(blueprint))
    # loop over all the servers of the topology and find out where we have this
    # service
    for server_name, server_dict in topology_dict["servers"].items():
        if "services" in server_dict:
            # print(yaml.dump(blueprint))
            for this_server_service in server_dict["services"]:
                # the default cluster name is 'common'
                this_cluster_name = "common"
                if "cluster" in this_server_service:
                    this_cluster_name = this_server_service["cluster"]

                if this_cluster_name not in blp_service_dict["clusters"]:
                    # here we set the cluster section of this server.
                    blp_service_dict["clusters"][this_cluster_name] = {}
                    blp_service_dict["clusters"][this_cluster_name]["servers"] = {}
                    blp_service_dict["clusters"][this_cluster_name][
                        "settings"
                    ] = copy.deepcopy(plf_service_settings)
                # print(yaml.dump(blueprint))
                blp_cluster = blp_service_dict["clusters"][this_cluster_name]
                if server_name not in blp_cluster["servers"]:
                    blp_cluster["servers"][server_name] = {}
                    blp_cluster["servers"][server_name]["settings"] = {}
                # print(yaml.dump(blueprint))
                try:
                    for prop_key, prop_value in settings_dict["services"][service_name][
                        "clusters"
                    ][this_cluster_name]["settings"].items():
                        blp_cluster["settings"][prop_key] = prop_value
                except KeyError:
                    pass
                # print(yaml.dump(blueprint))
                try:
                    for prop_key, prop_value in blp_cluster["settings"].items():
                        blp_cluster["servers"][server_name]["settings"][
                            prop_key
                        ] = prop_value
                except KeyError:
                    pass
                try:
                    for prop_key, prop_value in server_dict["settings"].items():
                        blp_cluster["servers"][server_name]["settings"][
                            prop_key
                        ] = prop_value
                except KeyError:
                    pass
                # print(yaml.dump(blueprint))


def compute_blueprint_setting(
    blueprint: Dict[str, Any],
    settings_dict: Dict[str, Any],
    topology_dict: Dict[str, Any],
) -> None:
    """Compute the blueprint settings at all three levels: platform, cluster and server.

    :param blueprint:  the blueprint to fill
    :param settings_dict: the user settings dictionary. It contains platform and cluster wide settings
    :param topology_dict: the user topology dictionary, It contains the servers dictionary
    :return:
    """

    if "services" in settings_dict:
        for service_name, service_dict in settings_dict["services"].items():
            compute_blueprint_service_settings(
                blueprint, service_name, settings_dict, topology_dict
            )


def compute_blueprint_versions(blueprint: Dict[str, Any], deployer_path: str) -> None:
    """Add the version to each service settings.

    This is only performed if the service is known to the punch deployer and if a version
    is not already specified in there.

    :param deployer_path:
    :param blueprint:
    :return:
    """
    versions_dict = ansible_templating_utils.get_components_version(deployer_path)
    for service_name, service in blueprint["services"].items():
        if "version" not in service["settings"]:
            if service_name in versions_dict:
                service["settings"]["version"] = versions_dict[service_name]


def compute_blueprint_users(blueprint, topology_dict) -> None:
    """Compute the blueprint users.

    Keyword arguments:
        blueprint -- the blueprint to fill
        settings_dict -- the user settings dictionary. It contains platform and cluster wide settings
        topology_dict -- the user topology dictionary, It contains the servers dictionary
    """
    blueprint["users"] = {}
    if "servers" in topology_dict:
        for host, item in topology_dict["servers"].items():
            if "users" in item:
                for s in item["users"]:
                    settings = {}
                    user = None
                    for key, value in s.items():
                        if key == "user":
                            user = s[key]
                        elif key == "settings":
                            settings = s[key]
                        else:
                            raise click.BadParameter(
                                "only 'user' and 'settings' keys are allowed for server 'users'"
                            )
                    if user not in blueprint["users"]:
                        blueprint["users"][user] = {}
                    blueprint["users"][user] = copy.deepcopy(settings)
