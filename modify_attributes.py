# -*- coding: utf-8 -*-

from tools.service_instance import LDAP
from tools import cli


def modify_info(ldap_obj, args):
    """
    更改用户 uid, 附带更改更 UID 相关的所有属性.
    :param ldap_obj: LDAP 实例
    :param args: 所有参数
    :return:
    """
    # 更改的参数需要传入 list,所以直接在外部处理好数据格式.
    # 涉及到判断用户是否存在的公共方法,不对其进行格式处理
    replace_json = {
        "search_string": "{}".format(args.user_name),  # 默认搜索字符串
        "ou": args.ou_name,
        "uid": "{}".format(args.user_name),
        "replace_uid": args.new_user
    }

    data = ldap_obj.get_users(**replace_json)

    ret = ldap_obj.modify_uid(*data, **replace_json)

    if ret == 1:
        print("Modify User OK")
    else:
        print(ret)


if __name__ == '__main__':
    parser = cli.Parser()

    parser.add_optional_arguments(cli.Argument.USER_NAME, cli.Argument.RE_USER_NAME, cli.Argument.OU_NAME)

    args = parser.get_args()

    ldap_obj = LDAP(args)

    modify_info(ldap_obj, args)
