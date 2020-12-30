#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses


@dataclasses.dataclass()
class SourceHierarchy(object):

    source_settings_dir: str
    profile: str
    settings_yml_file: str = dataclasses.field(init=False)
    topology_yml_file: str = dataclasses.field(init=False)
    resolv_yml_file: str = dataclasses.field(init=False)
    vagrant_j2_file: str = dataclasses.field(init=False)
    template_dir: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.settings_yml_file = (
            f"{self.source_settings_dir}/conf/profiles/{self.profile}/settings.yml"
        )
        self.topology_yml_file = (
            f"{self.source_settings_dir}/conf/profiles/{self.profile}/topology.yml"
        )
        self.resolv_yml_file = (
            f"{self.source_settings_dir}/conf/profiles/{self.profile}/resolv.yml"
        )
        self.vagrant_j2_file = f"{self.source_settings_dir}/conf/vagrant/Vagrantfile.j2"
        self.template_dir = f"{self.source_settings_dir}/conf/deployment_templates/"
