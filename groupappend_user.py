# -*- coding: utf-8 -*-

from tools.service_instance import LDAP
from tools import cli


def add_user_group(ldap_obj, args):
    """
    将用户添加到组,或者将用户从组中删除
    :param ldap_obj: LDAP 实例
    :param args: 外部所有参数
    :return:
    """

    data_json = {
        "search_string": args.group_name,  # 默认搜索字符串
        "ou": "Groups",  # 在什么 OU 下操作
        "cn": args.group_name,  # 要操作的组名
        "action": args.action,  # 准备什么操作
        "memberUid": [args.user_name],  # 准备要操作的用户名
        "user_type": args.user_type,  # 设置用户使用的类型 Linux or Wiki
        "uniqueMember": None
    }

    data = ldap_obj.get_groups()

    ret = ldap_obj.UserToGroup(*data, **data_json)

    if ret == 1:
        print("{} User {} To {} OK".format(data_json.get('action'), data_json.get('memberUid')[0], data_json.get('cn')))
    else:
        print("ret=", ret)


if __name__ == '__main__':
    parser = cli.Parser()

    parser.add_optional_arguments(cli.Argument.USER_NAME, cli.Argument.GROUP_NAME, cli.Argument.CUS_ACTION,
                                  cli.Argument.USER_TYPE)

    args = parser.get_args()

    ldap_obj = LDAP(args)

    add_user_group(ldap_obj, args)
