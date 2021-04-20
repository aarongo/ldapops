# -*- coding: utf-8 -*-
import argparse
import getpass
from config.con_conf import *

__author__ = "ModeYl"


class Parser:
    def __init__(self):
        self._parser = argparse.ArgumentParser(description='Arguments for talking to LDAP')
        self._standard_args_group = self._parser.add_argument_group('standard arguments')
        self._specific_args_group = self._parser.add_argument_group('sample-specific arguments')

        # because -h is reserved for 'help' we use -s for service
        self._standard_args_group.add_argument('-s', '--host',
                                               required=False,
                                               type=str,
                                               default=get_config_parameter('LDAP_HOST'),
                                               action='store',
                                               help='LDAP service address to connect to')

        # because we want -p for password, we use -o for port
        self._standard_args_group.add_argument('-o', '--port',
                                               required=False,
                                               type=int,
                                               default=389,
                                               action='store',
                                               help='Port to connect on')

        self._standard_args_group.add_argument('-u', '--user',
                                               required=False,
                                               type=str,
                                               default=get_config_parameter('LDAP_USER'),
                                               action='store',
                                               help='User name to use when connecting to host')

        self._standard_args_group.add_argument('-p', '--password',
                                               required=False,
                                               default=get_config_parameter('LDAP_PASSWORD'),
                                               action='store',
                                               help='Password to use when connecting to host')

        self._standard_args_group.add_argument('-b', '--base_dc',
                                               required=False,
                                               default=get_config_parameter('LDAP_BASE_DC'),
                                               action='store',
                                               help='Base bc to use when connecting to host')

    def get_args(self):
        """
        Supports the command-line arguments needed to form a connection to vSphere.
        """
        args = self._parser.parse_args()
        return self._prompt_for_password(args)

    def _add_sample_specific_arguments(self, is_required: bool, *args):
        """
        Add an argument to the "sample specific arguments" group
        Requires a predefined argument from the Argument class.
        """
        for arg in args:
            name_or_flags = arg["name_or_flags"]
            options = arg["options"]
            options["required"] = is_required
            self._specific_args_group.add_argument(*name_or_flags, **options)

    def add_optional_arguments(self, *args):
        """
        Add an optional argument to the "sample specific arguments" group.
        Requires a predefined argument from the Argument class.
        """
        self._add_sample_specific_arguments(False, *args)

    def _prompt_for_password(self, args):
        """
        if no password is specified on the command line, prompt for it
        """
        if not args.password:
            args.password = getpass.getpass(
                prompt='"--password" not provided! Please enter password for host %s and user %s: '
                       % (args.host, args.user))
        return args


class Argument:
    def __init__(self):
        pass

    USER_NAME = {
        'name_or_flags': ['-n', '--user_name'],
        'options': {'action': 'store', 'help': '操作的用户名'}
    }

    GROUP_NAME = {
        'name_or_flags': ['-g', '--group_name'],
        'options': {'action': 'store', 'help': '操作的用户组'}
    }

    GROUP_NUMBER = {
        'name_or_flags': ['-i', '--gid'],
        'options': {'action': 'store', 'type': int, 'default': 505, 'help': '设置组 ID'}
    }

    ADMIN = {
        'name_or_flags': ['--admin'],
        'options': {'action': 'store_true', 'help': '是否是LDAP Admin 默认是普通用户,加上该参数是管理员'}
    }

    OU_NAME = {
        'name_or_flags': ['-ou', '--ou_name'],
        'options': {'action': 'store', 'help': '操作的 OU 名'}
    }

    SECONDARY_GROUP_NAME = {
        'name_or_flags': ['-se', '--secondary_name'],
        'options': {'action': 'store', 'help': '操作的二级组名'}
    }

    ACTION_LEVEL = {
        'name_or_flags': ['-l', '--level'],
        'options': {'action': 'store', 'type': int, 'help': '操作级别'}
    }

    CUS_ACTION = {
        'name_or_flags': ['-ac', '--action'],
        'options': {'action': 'store', 'help': '执行什么操作 包含 append,remove'}
    }

    USER_TYPE = {
        'name_or_flags': ['-t', '--user_type'],
        'options': {'action': 'store', 'type': int, 'help': '用户的类型 1: Linux 2: Wiki'}
    }

    RE_USER_NAME = {
        'name_or_flags': ['-re', '--new_user'],
        'options': {'action': 'store', 'help': '新用户名称'}
    }

    ATTRIBUTE_NAME = {
        'name_or_flags': ['-an', '--attribute_name'],
        'options': {'action': 'store', 'help': '准备更改的属性名称'}
    }

    ATTRIBUTE_VALUE = {
        'name_or_flags': ['-av', '--attribute_value'],
        'options': {'action': 'store', 'help': '准备更改的属性值'}
    }