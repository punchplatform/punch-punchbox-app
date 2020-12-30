#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import ClassVar
from typing import Tuple


class CommandOption(object):

    DEPLOYER_OPT: ClassVar[str] = "--deployer"
    TOPOLOGY_OPT: ClassVar[str] = "--topology"
    WORKSPACE_OPT: ClassVar[str] = "--workspace"
    PROFILE_OPT: ClassVar[str] = "--profile"
    SETTINGS_OPT: ClassVar[str] = "--settings"
    OUTPUT_OPT: ClassVar[str] = "--output"
    BLUEPRINT_OPT: ClassVar[str] = "--blueprint"
    TEMPLATE_OPT: ClassVar[str] = "--template"
    YES_OPT: ClassVar[Tuple[str, ...]] = ("--yes", "-y")
    VERBOSE_OPT: ClassVar[Tuple[str, ...]] = ("--verbose", "-v")
