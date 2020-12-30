#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from typing import Callable
from typing import Dict

import pytest

from _pytest.monkeypatch import MonkeyPatch

from punchbox.common_lib.runtime_meta import environment


class TestEnvironment(object):

    FAKE_ENV: Dict[str, str] = {
        environment.Environment.PUNCHPLATFORM_PUNCHBOX_INSTALL_DIR: "/tmp/fake"
    }

    def test_environment_not_exists(self) -> None:
        """
        Test if correct value is returned when ENV does not exist
        """

        assert environment.Environment.punchbox_install_dir() == os.getcwd()

    @pytest.fixture()
    def set_env(self, monkeypatch: MonkeyPatch) -> None:
        for _key, _value in TestEnvironment.FAKE_ENV.items():
            key: str = _key
            value: str = _value
            monkeypatch.setenv(key, value)

    def test_environment_exists(self, set_env: Callable[[MonkeyPatch], None]) -> None:
        install_dir: str = environment.Environment.PUNCHPLATFORM_PUNCHBOX_INSTALL_DIR
        assert (
            environment.Environment.punchbox_install_dir() == self.FAKE_ENV[install_dir]
        )
