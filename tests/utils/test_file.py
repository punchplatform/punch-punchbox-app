#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import ClassVar

from typing_extensions import Final

from punchbox.common_lib.data_classes import punchbox_configuration
from punchbox.utils import file


class TestFile(object):

    sample_punchbox_file_path: ClassVar[Final[str]] = "./conf/samples/punchbox.yml"

    def test_punchbox_settings_serialization(self) -> None:
        """
        Test if punchbox yaml file serialization is made correctly
        """
        punchbox: punchbox_configuration.Punchbox = file.File.read_punchbox_settings_file(
            TestFile.sample_punchbox_file_path
        )
        assert punchbox.version == "1.0"
        assert punchbox.env.workspace == "/tmp/hello12345"
        assert (
            punchbox.punch.user_settings == "/tmp/hello12345/conf/punchbox/settings.yml"
        )
        assert punchbox.vagrant.vagrantfile == "/tmp/hello12345/vagrant/Vagrantfile"
