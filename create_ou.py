# -*- coding: utf-8 -*-

from tools.service_instance import LDAP
from tools import cli


def ou(ldap_obj, args):
    """

    :param: ldap_obj: Ldap 实例化
    :param args: 外部所有参数
    :return:
    """
    create_ou_json = {
        "search_string": "{}".format(args.ou_name),  # 默认搜索字符串
        "ou": "{}".format(args.ou_name),
        "object_class": ['top', 'organizationalUnit'],
        "attribute": {'ou': '{}'.format(args.ou_name)}
    }
    data = ldap_obj.get_ou(**create_ou_json)

    create_ou = ldap_obj.create_group_ou(*data, **create_ou_json)
    if create_ou == 1:
        print("Create Ou OK")
    else:
        print(create_ou)


if __name__ == '__main__':
    parser = cli.Parser()

    parser.add_optional_arguments(cli.Argument.OU_NAME)

    args = parser.get_args()

    print(args)

    ldap_obj = LDAP(args)

    # ou(ldap_obj, args)
