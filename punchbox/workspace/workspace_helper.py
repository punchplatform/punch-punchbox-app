#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from typing import List

from punchbox.common_lib.data_classes import source_hierarchy
from punchbox.common_lib.data_classes import workspace_hierarchy
from punchbox.utils.file import File


class WorkspaceHelper(object):
    def __init__(self) -> None:
        """static class"""
        ...

    @staticmethod
    def create_workspace_hierarchy(
        work_struct: workspace_hierarchy.WorkspaceHierarchy,
    ) -> None:
        File.create_dir_if_needed(
            (
                work_struct.template_dir,
                work_struct.punchbox_conf_dir,
                work_struct.pp_conf_dir,
                work_struct.vagrant_dir,
                work_struct.generated_conf_dir,
            )
        )

    @staticmethod
    def duplicate_required_files(
        source_struct: source_hierarchy.SourceHierarchy,
        work_struct: workspace_hierarchy.WorkspaceHierarchy,
    ) -> None:
        File.copy_to_workspace(
            source_struct.topology_yml_file, work_struct.dest_topology_yml_file,
        )
        File.copy_to_workspace(
            source_struct.settings_yml_file, work_struct.dest_settings_yml_file,
        )
        File.copy_to_workspace(
            source_struct.resolv_yml_file, work_struct.dest_resolv_yml_file,
        )
        File.copy_to_workspace(
            source_struct.vagrant_j2_file, work_struct.dest_vagrant_j2_file,
        )

    @staticmethod
    def apply_templating_required_files(
        source_struct: source_hierarchy.SourceHierarchy,
        work_struct: workspace_hierarchy.WorkspaceHierarchy,
    ) -> None:
        template_dir: str = os.path.abspath(source_struct.template_dir)
        src_files: List[str] = os.listdir(template_dir)
        for _file_name in src_files:
            file_name: str = _file_name
            full_file_name: str = os.path.join(template_dir, file_name)
            if os.path.isfile(full_file_name):
                File.copy_to_workspace(full_file_name, work_struct.template_dir)
