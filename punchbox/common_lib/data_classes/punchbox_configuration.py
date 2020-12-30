#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses
import os

from punchbox.common_lib.data_classes.workspace_hierarchy import WorkspaceHierarchy


@dataclasses.dataclass()
class Env(object):
    deployer: str
    type: str
    vagrantfile: str
    workspace: str


@dataclasses.dataclass()
class Punch(object):
    blueprint: str
    deployment_settings: str
    deployment_settings_template: str
    punchplatform_deployment_settings: str
    resolv_conf: str
    resolv_conf_template: str
    user_resolver: str
    user_settings: str
    user_topology: str


@dataclasses.dataclass()
class Vagrant(object):
    template: str
    vagrantfile: str


@dataclasses.dataclass()
class Punchbox(object):
    version: str
    env: Env
    punch: Punch
    vagrant: Vagrant

    def __post_init__(self) -> None:
        if self.version is None or "":
            raise TypeError("Missing version in your punchbox yaml configuration")
        if isinstance(self.env, dict):
            self.env = Env(**self.env)
        if isinstance(self.punch, dict):
            self.punch = Punch(**self.punch)
        if isinstance(self.vagrant, dict):
            self.vagrant = Vagrant(**self.vagrant)


@dataclasses.dataclass()
class PunchboxConfiguration(object):

    workspace_hierarchy: WorkspaceHierarchy
    workspace_type: str
    deployer_zip_path: str
    punchbox_configuration: Punchbox = dataclasses.field(init=False)
    punchbox_configuration_dict: dict = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.punchbox_configuration = Punchbox(
            version="1.0",
            env=self.__env(),
            punch=self.__punch(),
            vagrant=self.__vagrant(),
        )
        self.punchbox_configuration_dict = dataclasses.asdict(
            self.punchbox_configuration
        )

    def __env(self) -> Env:
        return Env(
            deployer=self.deployer_zip_path,
            type=self.workspace_type,
            workspace=os.path.abspath(self.workspace_hierarchy.workspace_path),
            vagrantfile=os.path.abspath(self.workspace_hierarchy.target_vagrant_file),
        )

    def __vagrant(self) -> Vagrant:
        return Vagrant(
            template=os.path.abspath(self.workspace_hierarchy.dest_vagrant_j2_file),
            vagrantfile=os.path.abspath(self.workspace_hierarchy.target_vagrant_file),
        )

    def __punch(self) -> Punch:
        return Punch(
            blueprint=os.path.abspath(
                self.workspace_hierarchy.target_blueprint_yml_file
            ),
            user_topology=os.path.abspath(
                self.workspace_hierarchy.dest_topology_yml_file
            ),
            user_settings=os.path.abspath(
                self.workspace_hierarchy.dest_settings_yml_file
            ),
            user_resolver=os.path.abspath(
                self.workspace_hierarchy.dest_resolv_yml_file
            ),
            deployment_settings_template=os.path.abspath(
                self.workspace_hierarchy.target_deployment_settings_yml_j2_file
            ),
            deployment_settings=os.path.abspath(
                self.workspace_hierarchy.target_deployment_settings_yml_file
            ),
            punchplatform_deployment_settings=os.path.abspath(
                self.workspace_hierarchy.target_legacy_deployment_settings
            ),
            resolv_conf=os.path.abspath(
                f"{self.workspace_hierarchy.pp_conf_dir}/resolv.hjson"
            ),
            resolv_conf_template=os.path.abspath(
                f"{self.workspace_hierarchy.template_dir}/resolv.hjson.j2"
            ),
        )
