#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import sys


class PunchUtils(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def print_usage(argument: str):
        click.echo(
            """
            Usage:
                {} <templateFileName.j2> {{jsonCustomisationDictionary}}\n
                or\n
                {} <templateFileName.j2> -f <json property file>\n
            """.format(
                argument, argument
            ),
            err=True,
        )


if __name__ == "__main__":

    # examples of using PunchUtils
    print("################# Example 1 #################")
    argument: str = "ls -lf /tmp"
    PunchUtils.print_usage(argument)
    print("################# END #################")
