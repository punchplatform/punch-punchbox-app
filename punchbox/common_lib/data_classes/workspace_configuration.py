#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dataclasses


@dataclasses.dataclass()
class WorkspaceConfiguration(object):

    profile: str
    workspace_type: str = "deployed"

    def __post_init__(self) -> None:
        if self.profile == "standalone":
            self.workspace_type = "standalone"


if __name__ == "__main__":

    test1: WorkspaceConfiguration = WorkspaceConfiguration(profile="standalone")
    test2: WorkspaceConfiguration = WorkspaceConfiguration(profile="deployed")

    assert test1.workspace_type == "standalone"
    assert test2.workspace_type == "deployed"
