#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses


@dataclasses.dataclass()
class WorkspaceHierarchy(object):

    workspace_path: str
    conf_dir: str = dataclasses.field(init=False)
    punchbox_conf_dir: str = dataclasses.field(init=False)
    generated_conf_dir: str = dataclasses.field(init=False)
    pp_conf_dir: str = dataclasses.field(init=False)
    vagrant_dir: str = dataclasses.field(init=False)
    template_dir: str = dataclasses.field(init=False)
    dest_vagrant_j2_file: str = dataclasses.field(init=False)
    dest_settings_yml_file: str = dataclasses.field(init=False)
    dest_topology_yml_file: str = dataclasses.field(init=False)
    dest_resolv_yml_file: str = dataclasses.field(init=False)
    target_vagrant_file: str = dataclasses.field(init=False)
    target_blueprint_yml_file: str = dataclasses.field(init=False)
    target_workspace_yml_file: str = dataclasses.field(init=False)
    target_deployment_settings_yml_file: str = dataclasses.field(init=False)
    target_deployment_settings_yml_j2_file: str = dataclasses.field(init=False)
    target_legacy_deployment_settings: str = dataclasses.field(init=False)
    activate_sh_file: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.conf_dir = f"{self.workspace_path}/conf"
        self.punchbox_conf_dir = f"{self.conf_dir}/punchbox"
        self.generated_conf_dir = f"{self.punchbox_conf_dir}/generated"
        self.pp_conf_dir = f"{self.workspace_path}/pp-conf"
        self.vagrant_dir = f"{self.workspace_path}/vagrant"
        self.template_dir = f"{self.generated_conf_dir}/conf/deployment_templates"
        self.dest_vagrant_j2_file = f"{self.vagrant_dir}/Vagrantfile.j2"
        self.dest_settings_yml_file = f"{self.punchbox_conf_dir}/settings.yml"
        self.dest_topology_yml_file = f"{self.punchbox_conf_dir}/topology.yml"
        self.dest_resolv_yml_file = f"{self.punchbox_conf_dir}/resolv.yml"
        self.target_vagrant_file = f"{self.vagrant_dir}/Vagrantfile"
        self.target_blueprint_yml_file = f"{self.generated_conf_dir}/blueprint.yml"
        self.target_workspace_yml_file = f"{self.punchbox_conf_dir}/punchbox.yml"
        self.target_deployment_settings_yml_file = (
            f"{self.pp_conf_dir}/deployment-settings.yml"
        )
        self.target_deployment_settings_yml_j2_file = (
            f"{self.template_dir}/deployment.settings.j2"
        )
        self.target_legacy_deployment_settings = (
            f"{self.pp_conf_dir}/punchplatform-deployment.settings"
        )
        self.activate_sh_file = f"{self.workspace_path}/activate.sh"
