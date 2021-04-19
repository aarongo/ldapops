# -*- coding: utf-8 -*-
from ldap3 import Server, Connection, SAFE_SYNC, ALL, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, HASHED_SALTED_SHA
from ldap3.utils.hashed import hashed

from src.manager_parameter import *
import random


def get_random_number_str(length):
    """
    生成随机数字字符串
    :param length: 字符串长度
    :return:
    """
    num_str = ''.join(str(random.choice(range(10))) for _ in range(length))
    return num_str


def ldap_search(*args, **kwargs):
    """
    私有方法,抽离处判断组信息是否存在 LDAP 已有组信息内
    :param args: LDAP 组信息--LIST
    :param kwargs: 准备创建的组信息--Dict
    :return: Boolean
    """

    # 判断要创建的是否组名是否已经存在
    # search_string = None
    # if 'ou' in kwargs:
    #     search_string = kwargs.get('ou')
    # elif 'uid' in kwargs:
    #     search_string = kwargs.get('uid')

    search_string = kwargs.get('search_string')

    exist = False
    # 将传入的数据进行分解后,每个元素的类型是<class 'ldap3.utils.ciDict.CaseInsensitiveDict'>, 在继续判读要创建的组是否存在.
    for i in args:
        for k, v in i.items():
            # if v[0] == search_string:
            # 判断要搜索的字符串是否在列表中即可
            if search_string in v:
                exist = True
    return exist


class LDAPHandler:
    def __init__(self):
        self.USER = get_config_parameter('LDAP_USER')

        self.PASSWORD = get_config_parameter('LDAP_PASSWORD')

        self.SERVER = Server(get_config_parameter('LDAP_HOST'), get_info=ALL)

        self.conn = Connection(self.SERVER, self.USER, self.PASSWORD, client_strategy=SAFE_SYNC, auto_bind=True)

    def get_users(self, **kwargs):
        """

        :return: LIST: 操作的响应结果,包含 UID
        """
        # status: 操作是否成功 result: 操作的结果 response: 操作的响应结果 request: 原始发送的请求
        status, result, response, _ = self.conn.search('ou={},dc=magic,dc=com'.format(kwargs.get('ou')),
                                                       '(objectclass=posixAccount)',
                                                       attributes=['uid'])  # attributes 限制查询出来的属性包括

        data = [row['attributes'] for row in response]

        return data

    def get_ou(self):
        """
        获取顶级所有 OU信息
        :return:
        """

        search_filter = '(objectclass=organizationalUnit)'

        status, result, response, _ = self.conn.search(get_config_parameter('LDAP_BASE_DC'),
                                                       search_filter, attributes=['ou'])

        data = [row['attributes'] for row in response]

        return data

    def get_groups(self):
        """
        获取 Groups ou 下所有组信息
        :return: 返回所有组信息
        """
        search_filter = '(|(objectclass=posixGroup)(objectclass=groupOfUniqueNames))'

        status, result, response, _ = self.conn.search('ou=Groups,dc=magic,dc=com', search_filter, attributes=['cn'])

        data = [row['attributes'] for row in response]

        return data

    def create_group_ou(self, *args, **kwargs):
        """
        创建顶层 ou
        :param args: 传入的组信息
        :param kwargs: 传入要创建组信息,包括组名 角色类 具体参数值
        :return:
        """
        # 传入*args **kwargs目的,将变量直接处理成 数组和 dict
        if not ldap_search(*args, **kwargs):
            ou = kwargs.get('ou')
            dn = "ou={},{}".format(ou, get_config_parameter('LDAP_BASE_DC'))
            object_class = kwargs.get('object_class')
            attribute = kwargs.get('attribute')
            status, result, response, _ = self.conn.add(dn, object_class, attribute)
            # 如果创建成功直接返回 True,如果失败返回失败描述
            if status:
                return 1
            else:
                return result['description']
        else:
            return {"description": "OU is Exist"}

    def create_group_cn(self, *args, **kwargs):
        """
        创建顶层 ou下 cn
        :param args: 传入的组信息
        :param kwargs: 传入要创建组信息,包括组名 角色类 具体参数值
        :return:
        """
        # 传入*args **kwargs目的,将变量直接处理成 数组和 dict
        if not ldap_search(*args, **kwargs):
            ou = kwargs.get('ou')
            cn = kwargs.get('cn')
            dn = "cn={},ou={},{}".format(cn, ou, get_config_parameter('LDAP_BASE_DC'))
            objectclass = kwargs.get('objectclass')
            attribute = kwargs.get('attribute')
            status, result, response, _ = self.conn.add(dn, objectclass, attribute)
            # 如果创建成功直接返回 True,如果失败返回失败描述
            if status:
                return 1
            else:
                return result['description']
        else:
            return {"description": "CN already exists under Group"}

    def delete_group(self, *args, **kwargs):
        """

        :param args: 传入的组信息
        :param kwargs: 传入要创建组信息,包括组名 角色类 具体参数值
        :return:
        """
        # 传入*args **kwargs目的,将变量直接处理成 数组和 dict
        if ldap_search(*args, **kwargs):
            row = kwargs.get('row')
            dn = "{},{}".format(row, get_config_parameter('LDAP_BASE_DC'))
            status, result, response, _ = self.conn.delete(dn)
            # 如果创建成功直接返回 True,如果失败返回失败描述
            if status:
                return 1
            else:
                return result['description']
        else:
            return {"description": "Group Is Not Found"}

    def create_user(self, *args, **kwargs):
        """

        :param args: 已经存在的所有用户信息
        :param kwargs: 要创建的用户信息以及属性信息
        :return:
        """

        if not ldap_search(*args, **kwargs):
            ou = "ou={}".format(kwargs.get('ou'))
            uid = "uid={}".format(kwargs.get('uid'))
            # 根据定义的用户角色生成不同的dn 信息
            if kwargs.get('is_admin'):
                cn = "cn={}".format(kwargs.get('attribute').get('cn'))
                dn = "{},{},{}".format(cn, ou, get_config_parameter('LDAP_BASE_DC'))
            else:
                dn = "{},{},{}".format(uid, ou, get_config_parameter('LDAP_BASE_DC'))
            object_class = kwargs.get('objectclass')
            attribute = kwargs.get('attribute')
            status, result, response, _ = self.conn.add(dn, object_class, attribute)
            if status:
                return 1
            else:
                return result['description']
        else:
            return {"description": "User Is Exist"}

    def delete_user(self, *args, **kwargs):
        """
        删除组内成员
        :param args: 所有用户的 LIST
        :param kwargs: 准备删除用户的信息
        :return:
        """

        if ldap_search(*args, **kwargs):
            ou = "ou={}".format(kwargs.get('ou'))
            uid = "uid={}".format(kwargs.get('uid'))
            dn = "{},{},{}".format(uid, ou, get_config_parameter('LDAP_BASE_DC'))
            status, result, response, _ = self.conn.delete(dn)
            # 如果创建成功直接返回 True,如果失败返回失败描述
            if status:
                return 1
            else:
                return result['description']
        else:
            return {"description": "User Is Not Found"}

    def modify_uid(self, *args, **kwargs):

        """
        更改用户名称
        :param args: 传入已经存在的用户列表
        :param kwargs: 要更改的属性
        :return:
        """

        if ldap_search(*args, **kwargs):
            ou = "ou=Users"
            # 待更改的 UID 名称
            old_uid = "uid={}".format(kwargs.get('uid'))
            # 拼接要更改的 DN
            dn = "{},{},{}".format(old_uid, ou, get_config_parameter('LDAP_BASE_DC'))
            # 更改后的 UID 名称
            new_uid = "uid={}".format(kwargs.get('replace_uid'))
            # 要先进行对主属性 UID 更新
            status, result, response, _ = self.conn.modify_dn(dn, new_uid)
            # 此方法直接进行替换主属性 UID 时不正常,只能进行删除与替换新增的,能替换原有的. 在替换时报"namingViolation"
            # 重新赋值 dn, 根据新的 dn 替换相关属性
            new_dn = "{},{},{}".format(new_uid, ou, get_config_parameter('LDAP_BASE_DC'))
            status, result, response, _ = self.conn.modify(new_dn, {'cn': [(MODIFY_REPLACE, kwargs.get('cn'))],
                                                                    'displayName': [
                                                                        (MODIFY_REPLACE, kwargs.get('displayName'))],
                                                                    'givenName': [
                                                                        (MODIFY_REPLACE, kwargs.get('givenName'))],
                                                                    'homeDirectory': [
                                                                        (MODIFY_REPLACE, kwargs.get('homeDirectory'))],
                                                                    'mail': [(MODIFY_REPLACE, kwargs.get('mail'))]})
            # print(self.conn.search(dn, '({})'.format(new_uid),
            #                        attributes=['uid', 'cn', 'givenName', 'givenName', 'homeDirectory', 'mail']))
            if status:
                return 1
            else:
                return result['description']
        else:
            return {"description": "User Not Found Can't Change"}

    def batch_modify_attribute(self, *args, **kwargs):
        """
        批量更改属性
        :param args: 获取所有用户
        :param kwargs: 更改用户的属性名称和值{}
        :return:
        """
        # 要更改什么组织下
        ou = kwargs.get('ou')

        ret = {}

        for name in args:
            dn = "uid={},{},{}".format(name.get('uid')[0], ou, get_config_parameter('LDAP_BASE_DC'))
            user_mail = "{}{}".format(name.get('uid')[0], kwargs.get('mail_suffix'))
            status, result, response, _ = self.conn.modify(dn, {'mail': [(MODIFY_REPLACE, user_mail)]})
            ret[name.get('uid')[0]] = result['description']
        return ret

    def HandlerUserToGroup(self, *args, **kwargs):
        group_name = kwargs.get('cn')
        ou_name = kwargs.get('ou')
        # 获取操作类型
        action = kwargs.get('action')
        # 拼接完成的 DN
        dn = "cn={},ou={},{}".format(group_name, ou_name, get_config_parameter('LDAP_BASE_DC'))

        # 判断组是否存在
        if ldap_search(*args, **kwargs):
            if action == 'add':
                if kwargs.get('user_type') == 'Linux':
                    status, result, response, _ = self.conn.modify(dn, {
                        'memberUid': [(MODIFY_ADD, kwargs.get('memberUid'))]})
                elif kwargs.get('user_type') == 'Wiki':
                    uniqueMember = [
                        "uid={},ou=Users,{}".format(kwargs.get('memberUid')[0],
                                                    get_config_parameter('LDAP_BASE_DC'))]  # 根据输入的类型拼接要处理的 dn
                    status, result, response, _ = self.conn.modify(dn, {
                        'uniqueMember': [(MODIFY_ADD, uniqueMember)]})

                    if status:
                        return 1
                    else:
                        return result['description']

            elif action == 'delete':
                if kwargs.get('user_type') == 'Linux':
                    status, result, response, _ = self.conn.modify(dn, {
                        'memberUid': [(MODIFY_DELETE, kwargs.get('memberUid'))]})
                elif kwargs.get('user_type') == 'Wiki':
                    uniqueMember = [
                        "uid={},ou=Users,{}".format(kwargs.get('memberUid')[0], get_config_parameter('LDAP_BASE_DC'))]
                    status, result, response, _ = self.conn.modify(dn, {'memberUid': [(MODIFY_DELETE, uniqueMember)]})

                    if status:
                        return 1
                    else:
                        return result['description']

            else:
                return {"description": "Unknown operation"}
        else:
            return {"description": "Group {} Not Exist".format(group_name)}
