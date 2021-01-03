#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil

from typing import Tuple

from punchbox.common_lib.data_classes import punchbox_configuration
from punchbox.common_lib.runtime_meta.key import Key
from punchbox.punch_entry_point.cli_configuration import PunchLogger


class File(object):
    """Static class"""

    def __init__(self) -> None:
        ...

    @staticmethod
    def copy_to_workspace(src: str, dst: str) -> None:
        """Copy a reference file to

        :param src: the src path
        :param dst: the destination path
        :return: None
        """
        if os.path.exists(os.path.abspath(dst)):
            PunchLogger().logger.info(
                f"[bold yellow]Overwriting {dst}[/]", extra={"markup": True}
            )
        shutil.copy(os.path.abspath(src), os.path.abspath(dst))

    @staticmethod
    def create_dir_if_needed(dirs: Tuple[str, ...]) -> None:
        """Create a bunch of directories

        :param dirs: one or several directory paths
        :return: None
        """
        for _d in dirs:
            d: str = _d
            if not os.path.exists(d):
                os.makedirs(d)

    @staticmethod
    def write_dict_as_yaml(path: str, content: dict) -> None:
        with open(path, "w+") as outfile:
            import yaml

            yaml.dump(content, outfile)

    @staticmethod
    def write_unicode_as_text_file(path: str, content: str) -> None:
        with open(path, "w+") as file:
            file.write(content)

    @staticmethod
    def read_punchbox_settings_file(path: str) -> punchbox_configuration.Punchbox:
        conf: dict = File.read_file_yaml_as_dict(path)
        vagrant: punchbox_configuration.Vagrant = punchbox_configuration.Vagrant(
            **conf[Key.VAGRANT]
        )
        env: punchbox_configuration.Env = punchbox_configuration.Env(**conf[Key.ENV])
        punch: punchbox_configuration.Punch = punchbox_configuration.Punch(
            **conf[Key.PUNCH]
        )
        version: str = conf[Key.VERSION]
        return punchbox_configuration.Punchbox(
            version=version, vagrant=vagrant, env=env, punch=punch
        )

    @staticmethod
    def read_file_yaml_as_dict(path: str) -> dict:
        import yaml

        conf: dict
        with open(path) as infile:
            conf = yaml.load(infile.read(), Loader=yaml.SafeLoader)
        return conf

    @staticmethod
    def remove_file_if_exist(path: str) -> str:
        if os.path.exists(path):
            os.remove(path)
            return f"Removed file: {path}"
        return f"File {path} does not exist, nothing to remove"


if __name__ == "__main__":

    # examples of using PunchUtils
    path_punchbox_yml: str = "./conf/samples/punchbox.yml"
    punchbox_yml: punchbox_configuration.Punchbox = File.read_punchbox_settings_file(
        path_punchbox_yml
    )
    print(punchbox_yml)
