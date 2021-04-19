# -*- coding: utf-8 -*-

from src.ldap_handler import *


def general_user_passwd(password):
    """
    生成用户密码
    :param password: str
    :return: 加密后的用户密码: 使用 ssha 形式
    """

    ret = hashed(HASHED_SALTED_SHA, password)

    return ret


def ou(name):
    """

    :param name: 要创建的 ou 名称
    :return:
    """
    create_ou_json = {
        "search_string": "{}".format(name),  # 默认搜索字符串
        "ou": "{}".format(name),
        "object_class": ['top', 'organizationalUnit'],
        "attribute": {'ou': '{}'.format(name)}
    }
    data = LDAP.get_ou()

    create_ou = LDAP.create_group_ou(*data, **create_ou_json)
    if create_ou == 1:
        print("Create Ou OK")
    else:
        print(create_ou)


def ou_cn(name):
    """

    :param name: 嵌套组的名称
    :return:
    """
    create_ou_cn_json = {
        "search_string": "{}".format(name),  # 默认搜索字符串
        'ou': 'Groups',  # 在哪个组下创建
        'cn': name,
        'objectclass': 'posixGroup',
        'attribute': {'cn': '{}'.format(name), 'gidNumber': get_random_number_str(5)}

    }

    data = LDAP.get_groups()

    create_ou_cn = LDAP.create_group_cn(*data, **create_ou_cn_json)

    if create_ou_cn == 1:
        print("Create OU of CN OK")
    else:
        print(create_ou_cn)


def delete_ou_or_cn(group_name, level):
    delete_ou_or_cn_json = {}
    data = None
    if level == 1:
        delete_ou_or_cn_json = {
            "search_string": "{}".format(group_name),  # 默认搜索字符串
            'row': 'ou={}'.format(group_name)  # 删除顶层 ou
        }
        data = LDAP.get_ou()  # 获取顶层 OU 信息
    elif level == 2:
        delete_ou_or_cn_json = {
            "search_string": "{}".format(group_name),  # 默认搜索字符串
            'row': 'cn={},ou={}'.format(group_name, "Groups")  # 删除OU 下 CN
        }
        data = LDAP.get_groups()  # 获取 Groups 下各组信息

    ret = LDAP.delete_group(*data, **delete_ou_or_cn_json)

    if ret == 1:
        print("Delete OU of CN OK")
    else:
        print(ret)


def create_user(name, group_name, is_admin):
    """
    创建普通用户与 ldap 管理员用户
    :param name: 用户名 str
    :param group_name: 在什么组下操作 str
    :param is_admin: 是不是管理员 boole
    :return:
    """

    if is_admin:
        objectclass = ['top', 'inetOrgPerson', 'person', 'shadowAccount', 'organizationalPerson']
        attribute = {
            "cn": "{}".format(name),
            "sn": "{}".format(name),
            "uid": "{}".format(name),
            "userPassword": general_user_passwd(name)
        }
    else:
        objectclass = ['top', 'inetOrgPerson', 'posixAccount', 'shadowAccount', 'organizationalPerson']
        attribute = {
            "cn": "{}".format(name),
            "sn": "Linux",
            "uid": "{}".format(name),
            "uidNumber": get_random_number_str(5),
            "gidNumber": 505,  # 组ID 在创建 Linux 用户是需要指定
            "homeDirectory": "/home/{}".format(name),
            "displayName": "{}".format(name),
            "givenName": "{}".format(name),
            "loginShell": "/bin/bash",
            "mail": "{}@magicengine.com.cn".format(name),
            "userPassword": general_user_passwd(name)
        }

    create_or_delete_user = {
        "search_string": "{}".format(name),  # 默认搜索字符串
        "admin": is_admin,
        "ou": "{}".format(group_name),
        "uid": "{}".format(name),
        "objectclass": objectclass,
        'attribute': attribute
    }

    data = LDAP.get_users(**create_or_delete_user)

    ret = LDAP.create_user(*data, **create_or_delete_user)

    if ret == 1:
        print("Create User OK")
    else:
        print(ret)


def delete_user(name, group_name):
    """

    :param name: 用户名
    :param group_name: 在什么组下操作
    :return:
    """

    create_or_delete_user = {
        "search_string": "{}".format(name),  # 默认搜索字符串
        "ou": "{}".format(group_name),
        "uid": "{}".format(name)
    }

    data = LDAP.get_users(**create_or_delete_user)

    ret = LDAP.delete_user(*data, **create_or_delete_user)

    if ret == 1:
        print("Delete User OK")
    else:
        print(ret)


def modify_info(name, replace_name):
    """
    更改用户 uid, 附带更改更 UID 相关的所有属性.
    :param name: 要操作的用户名
    :param replace_name: 准备替换的字段
    :return:
    """
    # 更改的参数需要传入 list,所以直接在外部处理好数据格式.
    # 涉及到判断用户是否存在的公共方法,不对其进行格式处理
    replace_json = {
        "search_string": "{}".format(name),  # 默认搜索字符串
        "uid": "{}".format(name),
        "cn": [replace_name],
        "displayName": [replace_name],
        "givenName": [replace_name],
        "homeDirectory": ['/home/{}'.format(replace_name)],
        "mail": ['{}@magicengine.com.cn'.format(replace_name)],
        "replace_uid": replace_name
    }

    data = LDAP.get_users()

    ret = LDAP.modify_uid(*data, **replace_json)

    if ret == 1:
        print("Modify User OK")
    else:
        print(ret)


def add_user_group(name, group_name, action, user_type):
    """
    将用户添加到组,或者将用户从组中删除
    :param name: 要操作的用户名
    :param group_name: 要在哪个组中操作
    :param action: 准备什么操作 [add, delete]
    :param user_type: 用户是什么类型, 是登陆服务器,还是使用文档平台
    :return:
    """

    data_json = {
        "search_string": group_name,  # 默认搜索字符串
        "ou": "Groups",  # 在什么 OU 下操作
        "cn": group_name,  # 要操作的组名
        "action": action,  # 准备什么操作
        "memberUid": [name],  # 准备要操作的用户名
        "user_type": user_type,  # 设置用户使用的类型 Linux or Wiki
        "uniqueMember": None
    }

    data = LDAP.get_groups()

    ret = LDAP.HandlerUserToGroup(*data, **data_json)

    if ret == 1:
        print("{} User {} To {} OK".format(data_json.get('action'), data_json.get('memberUid')[0], data_json.get('cn')))
    else:
        print(ret)


def modify_attribute():
    data = LDAP.get_users()

    modify_json = {
        'ou': "ou=Users",
        'mail_suffix': "@magicengine.com.cn"
    }

    ret = LDAP.batch_modify_attribute(*data, **modify_json)

    tmp = 0

    for k, v in ret:
        if v == "success":
            tmp += 1
    if tmp == 0:
        print("没有账户被更改")
    else:
        print("共{}被更改了mail_suffix".format(tmp))


if __name__ == '__main__':
    LDAP = LDAPHandler()

    # delete_ou_or_cn(group_name='administrators', level=2)

    # ou(name='manages')

    # ou_cn(name='administrators')

    # 创建LDAP管理员时,is_admin设置为 True, 组名设置为 managers
    # create_user(name="admin_yulong", group_name="managers", is_admin=True)

    # delete_user(name="ldapadmin", group_name="managers") # 删除时直接指定要操作的组即可

    # modify_info('pytest', "pytest1")

    # add_user_group('liufeng', 'jira-confluence-user', 'add', 'Wiki')

    # modify_attribute()
