# -*- coding: utf-8 -*-

from tools import cli
from tools.service_instance import LDAP


def modify_attribute(ldap_obj, args):
    """

    :param ldap_obj: LDAP 实例
    :param args: 外部所有参数
    :return:
    """
    modify_json = {
        'ou': args.ou_name,
        'will_attribute_name': args.attribute_name,
        'attribute_value': args.attribute_name,
        'mail_suffix': "@magicengine.com.cn"
    }

    data = ldap_obj.get_users(**modify_json)

    ret = ldap_obj.batch_modify_attribute(*data, **modify_json)

    tmp = 0

    for k, v in ret:
        if v == "success":
            tmp += 1
    if tmp == 0:
        print("没有账户被更改")
    else:
        print("共{}被更改了mail_suffix".format(tmp))


if __name__ == '__main__':
    parser = cli.Parser()

    parser.add_optional_arguments(cli.Argument.OU_NAME, cli.Argument.ATTRIBUTE_NAME, cli.Argument.ATTRIBUTE_VALUE)

    args = parser.get_args()

    ldap_obj = LDAP(args)

    modify_attribute(ldap_obj, args)
