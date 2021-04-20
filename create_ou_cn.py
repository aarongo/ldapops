# -*- coding: utf-8 -*-

from tools.serviceutil import *
from tools import cli
from tools.service_instance import LDAP


def ou_cn(ldap_obj, args):
    """

    :param ldap_obj: Ldap Ldap 实例化
    :param args: 外部所有参数
    :return:
    """
    create_ou_cn_json = {
        "search_string": "{}".format(args.secondary_name),  # 默认搜索字符串
        'ou': 'Groups',  # 在哪个组下创建
        'cn': args.secondary_name,
        'objectclass': 'posixGroup',
        'attribute': {'cn': '{}'.format(args.secondary_name), 'gidNumber': get_random_number_str(5)}
    }

    data = ldap_obj.get_groups()

    create_ou_cn = ldap_obj.create_group_cn(*data, **create_ou_cn_json)

    if create_ou_cn == 1:
        print("Create OU of CN OK")
    else:
        print(create_ou_cn)


if __name__ == '__main__':
    parser = cli.Parser()

    parser.add_optional_arguments(cli.Argument.SECONDARY_GROUP_NAME)

    args = parser.get_args()

    ldap_obj = LDAP(args)

    ou_cn(ldap_obj, args)
