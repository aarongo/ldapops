# -*- coding: utf-8 -*-

from tools.serviceutil import *
from tools import cli
from tools.service_instance import LDAP


def create_user(ldap_obj, args):
    """
    创建普通用户与 ldap 管理员用户
    :param ldap_obj: LDAP 实例
    :param args: 用户名 str
    :return:
    """
    if args.admin:
        objectclass = ['top', 'inetOrgPerson', 'person', 'shadowAccount', 'organizationalPerson']
        attribute = {
            "cn": "{}".format(args.user_name),
            "sn": "{}".format(args.user_name),
            "uid": "{}".format(args.user_name),
            "userPassword": general_user_passwd(args.user_name)
        }
    else:
        objectclass = ['top', 'inetOrgPerson', 'posixAccount', 'shadowAccount', 'organizationalPerson']
        attribute = {
            "cn": "{}".format(args.user_name),
            "sn": "Linux",
            "uid": "{}".format(args.user_name),
            "uidNumber": get_random_number_str(5),
            "gidNumber": args.gid,  # 组ID 在创建 Linux 用户是需要指定
            "homeDirectory": "/home/{}".format(args.user_name),
            "displayName": "{}".format(args.user_name),
            "givenName": "{}".format(args.user_name),
            "loginShell": "/bin/bash",
            "mail": "{}@magicengine.com.cn".format(args.user_name),
            "userPassword": general_user_passwd(args.user_name)
        }

    create_or_delete_user = {
        "search_string": "{}".format(args.user_name),  # 默认搜索字符串
        "admin": args.admin,
        "ou": "{}".format(args.group_name),
        "uid": "{}".format(args.user_name),
        "objectclass": objectclass,
        'attribute': attribute
    }

    data = ldap_obj.get_users(**create_or_delete_user)

    ret = ldap_obj.create_user(*data, **create_or_delete_user)

    if ret == 1:
        print("Create User OK")
    else:
        print(ret)


if __name__ == '__main__':
    parser = cli.Parser()

    # 添加额外参数
    parser.add_optional_arguments(cli.Argument.USER_NAME, cli.Argument.GROUP_NAME, cli.Argument.ADMIN,
                                  cli.Argument.GROUP_NUMBER)
    args = parser.get_args()

    # 实例化 LDAP 链接
    ldap_obj = LDAP(args)

    create_user(ldap_obj, args)
