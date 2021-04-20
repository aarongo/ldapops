# -*- coding: utf-8 -*-

from tools.service_instance import LDAP
from tools import cli


def delete_ou_or_cn(ldap_obj, args):
    """

    :param ldap_obj: LDAP 实例
    :param args: 外部所有参数
    :return:
    """
    delete_ou_or_cn_json = {}
    data = None
    if args.level == 1:
        delete_ou_or_cn_json = {
            "search_string": "{}".format(args.group_name),  # 默认搜索字符串
            'row': 'ou={}'.format(args.group_name)  # 删除顶层 ou
        }
        data = ldap_obj.get_ou()  # 获取顶层 OU 信息
    elif args.level == 2:
        delete_ou_or_cn_json = {
            "search_string": "{}".format(args.group_name),  # 默认搜索字符串
            'row': 'cn={},ou={}'.format(args.group_name, "Groups")  # 删除OU 下 CN
        }
        data = ldap_obj.get_groups()  # 获取 Groups 下各组信息

    ret = ldap_obj.delete_group(*data, **delete_ou_or_cn_json)

    if ret == 1:
        print("Delete OU of CN OK")
    else:
        print(ret)


if __name__ == '__main__':
    parser = cli.Parser()

    parser.add_optional_arguments(cli.Argument.GROUP_NAME, cli.Argument.ACTION_LEVEL)

    args = parser.get_args()

    ldap_obj = LDAP(args)

    delete_ou_or_cn(ldap_obj, args)
