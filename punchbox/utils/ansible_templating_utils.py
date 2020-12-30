#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import subprocess
from typing import Dict, List
import click
import logging
from copy import deepcopy
import jinja2
import json
import yaml
import sys
import os
import re
import socket
from punchbox import components
from punchbox import services

# This main module is used to render a jinja2 template
# the rendering environement is loaded with provided customisation data that
# must be provided as a json dictionnary string


class AnsibleJSONEncoder(json.JSONEncoder):
    """
    Simple encoder class to deal with JSON encoding of internal
    types like HostVars
    """

    def default(self, o):
        if isinstance(o):
            return dict(o)
        else:
            return super(AnsibleJSONEncoder, self).default(o)


def regex_subst(st, pat, repl):
    if isinstance(st, list):
        return [regex_subst(a_string, pat, repl) for a_string in st]
    return re.sub(pat, repl, st)


def url_to_port(st, default_port=None):
    port_string = re.sub(".*:([0-9]+).*", "\\1", st)
    if port_string == st:
        port_string = default_port
    return port_string


def url_to_path(st):
    path_string = re.sub("[^/]*/(.*)", "/\\1", st)
    if path_string == st:
        path_string = "/"
    return path_string


def url_to_host(st):
    if isinstance(st, list):
        return [url_to_host(a_string) for a_string in st]
    return re.sub(":.*", "", st)


@jinja2.contextfunction
def get_context(c):
    return c


def resolve_hostname_to_ip(st):
    ip = socket.gethostbyname(st)
    if ip == "":
        raise Exception("Could not resolve provided hostname '" + st + "'.")
    return ip


def remove_duplicates(mylist):
    return list(set[mylist])


def is_dict_empty(my_dict):
    return bool(my_dict)


def env_override(value, key):
    return os.getenv(key, value)


def to_json(a, *args, **kw):
    """Convert the value to JSON"""

    return json.dumps(a, cls=AnsibleJSONEncoder, *args, **kw)


def to_yaml(a, *args, **kw):
    return a


def to_basename(path):
    return os.path.basename(path)


def to_nice_yaml(a, indentation=4, line_breaker="\n", optional_indent=0, *args, **kw):
    """Make verbose, human readable yaml"""
    try:
        import simplejson
    except ImportError:
        pass
    transformed = yaml.safe_dump(
        a, indent=indentation, default_flow_style=False, line_break=line_breaker
    )
    shift = ""
    for i in range(optional_indent):
        shift = " " + shift
    transformed2 = ""
    for line in transformed.split("\n"):
        transformed2 += shift + line + "\n"
    return transformed2


def to_nice_json(a, indent=4, *args, **kw):
    """Make verbose, human readable JSON"""
    # python-2.6's json encoder is buggy (can't encode hostvars)
    if sys.version_info < (2, 7):
        try:
            import simplejson
        except ImportError:
            pass
        else:
            try:
                major = int(simplejson.__version__.split(".")[0])
            except:
                pass
            else:
                if major >= 2:
                    return simplejson.dumps(
                        a, indent=indent, sort_keys=True, *args, **kw
                    )

    try:
        return json.dumps(
            a, indent=indent, sort_keys=True, cls=AnsibleJSONEncoder, *args, **kw
        )
    except:
        # Fallback to the to_json filter
        return to_json(a, *args, **kw)


def load_template(template_filename):
    template_dir = os.path.dirname(template_filename)
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        undefined=jinja2.StrictUndefined,
        extensions=["jinja2.ext.do"],
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template_name = os.path.basename(template_filename)
    env.filters["jsonify"] = json.dumps
    env.filters["regex_subst"] = regex_subst
    env.filters["url_to_host"] = url_to_host
    env.filters["url_to_port"] = url_to_port
    env.filters["url_to_path"] = url_to_path
    env.filters["resolve_hostname_to_ip"] = resolve_hostname_to_ip
    env.filters["remove_duplicates"] = remove_duplicates
    env.filters["env_override"] = env_override
    env.filters["to_nice_json"] = to_nice_json
    env.filters["to_nice_yaml"] = to_nice_yaml
    env.filters["to_json"] = to_nice_json
    env.filters["to_yaml"] = to_yaml
    env.filters["to_basename"] = to_basename
    env.filters["is_dict_empty"] = is_dict_empty
    template = env.get_template(template_name)
    template.globals["context"] = get_context
    template.globals["callable"] = callable
    return template


def get_components_version(deployer_path: str) -> Dict[str, str]:
    """
    Return a map containing all component version
    """
    data = {}
    versionof_shell = os.path.join(deployer_path, "bin/punchplatform-versionof.sh")
    for component in components.COMPONENTS:
        cmd = "{0} --legacy {1}".format(versionof_shell, component)
        result = subprocess.check_output(cmd, shell=True)
        data[component] = result.decode("utf-8").rstrip()
    return data


def dict_to_string(dictionary: dict, file_format: str) -> str:
    """
    Format a dictionary
    :param dictionary: Dictionary to format
    :param file_format: Output format (json, yaml)
    """
    if file_format.lower() == "json":
        return json.dumps(dictionary, indent=4)
    elif file_format.lower() == "yaml":
        return yaml.safe_dump(dictionary)
    else:
        raise NotImplementedError(f"Unknown file format {file_format}")
