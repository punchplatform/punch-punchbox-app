#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import ClassVar


class Commands(object):

    CREATE_CMD: ClassVar[str] = "create"
    BUILD_CMD: ClassVar[str] = "build"
    AUDIT_CMD: ClassVar[str] = "audit"
    BLUEPRINT_CMD: ClassVar[str] = "blueprint"
    DEPLOYMENT_SETTINGS_CMD: ClassVar[str] = "deployment-settings"
    RESOLVER_CMD: ClassVar[str] = "resolver"
    VAGRANTFILE_CMD: ClassVar[str] = "vagrantfile"
