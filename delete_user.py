# -*- coding: utf-8 -*-

from tools import cli
from tools.service_instance import LDAP


def delete_user(ldap_ohj, args):
    """

    :param ldap_ohj: LDAP 链接实例化
    :param args: 传参集合
    :return:
    """

    delete_user = {
        "search_string": "{}".format(args.user_name),  # 默认搜索字符串
        "ou": "{}".format(args.group_name),
        "uid": "{}".format(args.user_name)
    }

    data = ldap_ohj.get_users(**delete_user)

    ret = ldap_ohj.delete_user(*data, **delete_user)

    if ret == 1:
        print("Delete User OK")
    else:
        print(ret)


if __name__ == '__main__':
    parser = cli.Parser()

    parser.add_optional_arguments(cli.Argument.USER_NAME, cli.Argument.GROUP_NAME)

    args = parser.get_args()

    ldap_obj = LDAP(args)

    delete_user(ldap_obj, args)
