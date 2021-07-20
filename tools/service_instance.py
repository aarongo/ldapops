# -*- coding: utf-8 -*-

__author__ = "Mode, YL"

from ldap3 import Server, Connection, SAFE_SYNC, ALL, MODIFY_ADD, MODIFY_DELETE, MODIFY_REPLACE
from tools.serviceutil import *


class LDAP:
    def __init__(self, args):
        # 定义 server
        self.s = Server(args.host, get_info=ALL)
        # 定义链接
        self.conn = Connection(self.s, args.user, args.password, client_strategy=SAFE_SYNC, auto_bind=True)

        # 获取所有参数
        self.args = args

    def get_users(self, **kwargs):
        """

        :return: LIST: 操作的响应结果,包含 UID
        """
        # status: 操作是否成功 result: 操作的结果 response: 操作的响应结果 request: 原始发送的请求
        status, result, response, _ = self.conn.search('ou={},{}'.format(kwargs.get('ou'), self.args.base_dc),
                                                       '(objectclass=posixAccount)',
                                                       attributes=['uid'])  # attributes 限制查询出来的属性包括

        data = [row['attributes'] for row in response]

        return data

    def get_ou(self, **kwargs):
        """
        获取顶级所有 OU信息
        :return:
        """

        search_filter = '(objectclass=organizationalUnit)'

        status, result, response, _ = self.conn.search(self.args.base_dc, search_filter, attributes=['ou'])

        data = [row['attributes'] for row in response]

        return data

    def get_groups(self):
        """
        获取 Groups ou 下所有组信息
        :return: 返回所有组信息
        """
        search_filter = '(|(objectclass=posixGroup)(objectclass=groupOfUniqueNames))'

        status, result, response, _ = self.conn.search('ou=Groups,{}'.format(self.args.base_dc), search_filter,
                                                       attributes=['cn'])

        data = [row['attributes'] for row in response]

        return data

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
            if kwargs.get('admin'):
                cn = "cn={}".format(kwargs.get('attribute').get('cn'))
                dn = "{},{},{}".format(cn, ou, self.args.base_dc)
            else:
                dn = "{},{},{}".format(uid, ou, self.args.base_dc)
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
            dn = "{},{},{}".format(uid, ou, self.args.base_dc)
            status, result, response, _ = self.conn.delete(dn)
            # 如果创建成功直接返回 True,如果失败返回失败描述
            if status:
                return 1
            else:
                return result['description']
        else:
            return {"description": "User Is Not Found"}

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
            dn = "ou={},{}".format(ou, self.args.base_dc)
            print(dn)
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
            dn = "cn={},ou={},{}".format(cn, ou, self.args.base_dc)
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
            dn = "{},{}".format(row, self.args.base_dc)
            status, result, response, _ = self.conn.delete(dn)
            # 如果创建成功直接返回 True,如果失败返回失败描述
            if status:
                return 1
            else:
                return result['description']
        else:
            return {"description": "Group Is Not Found"}

    def UserToGroup(self, *args, **kwargs):
        group_name = kwargs.get('cn')
        ou_name = kwargs.get('ou')
        # 获取操作类型
        action = kwargs.get('action')
        # 拼接完成的 DN
        dn = "cn={},ou={},{}".format(group_name, ou_name, self.args.base_dc)
        # 定义放回值信息
        status, result = None, None
        # 判断组是否存在
        if ldap_search(*args, **kwargs):
            if action == 'append':
                if kwargs.get('user_type') == 1:
                    status, result, response, _ = self.conn.modify(dn, {
                        'memberUid': [(MODIFY_ADD, kwargs.get('memberUid'))]})
                elif kwargs.get('user_type') == 2:
                    uniqueMember = [
                        "uid={},ou=Users,{}".format(kwargs.get('memberUid')[0], self.args.base_dc)]  # 根据输入的类型拼接要处理的 dn
                    status, result, response, _ = self.conn.modify(dn, {'uniqueMember': [(MODIFY_ADD, uniqueMember)]})

                if status:
                    return 1
                else:
                    return result['description']

            elif action == 'remove':
                if kwargs.get('user_type') == 1:
                    status, result, response, _ = self.conn.modify(dn, {
                        'memberUid': [(MODIFY_DELETE, kwargs.get('memberUid'))]})
                elif kwargs.get('user_type') == 2:
                    uniqueMember = [
                        "uid={},ou=Users,{}".format(kwargs.get('memberUid')[0], self.args.base_dc)]
                    status, result, response, _ = self.conn.modify(dn, {'memberUid': [(MODIFY_DELETE, uniqueMember)]})

                if status:
                    return 1
                else:
                    return result['description']

            else:
                return {"description": "Unknown operation"}
        else:
            return {"description": "Group {} Not Exist".format(group_name)}

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
            dn = "uid={},{},{}".format(name.get('uid')[0], ou, self.args.base_dc)
            user_mail = "{}{}".format(name.get('uid')[0], kwargs.get('mail_suffix'))
            status, result, response, _ = self.conn.modify(dn, {'mail': [(MODIFY_REPLACE, user_mail)]})
            ret[name.get('uid')[0]] = result['description']
        return ret

    def modify_uid(self, *args, **kwargs):

        """
        更改用户名称
        :param args: 传入已经存在的用户列表
        :param kwargs: 要更改的属性
        :return:
        """

        if ldap_search(*args, **kwargs):
            ou = "ou={}".format(kwargs.get('ou'))
            # 待更改的 UID 名称
            old_uid = "uid={}".format(kwargs.get('uid'))
            # 拼接要更改的 DN
            dn = "{},{},{}".format(old_uid, ou, self.args.base_dc)
            # 更改后的 UID 名称
            new_uid = "uid={}".format(kwargs.get('replace_uid'))
            # 要先进行对主属性 UID 更新
            status, result, response, _ = self.conn.modify_dn(dn, new_uid)
            # 此方法直接进行替换主属性 UID 时不正常,只能进行删除与替换新增的,能替换原有的. 在替换时报"namingViolation"
            # 重新赋值 dn, 根据新的 dn 替换相关属性
            new_dn = "{},{},{}".format(new_uid, ou, self.args.base_dc)
            status, result, response, _ = self.conn.modify(new_dn, {'cn': [(MODIFY_REPLACE, kwargs.get('replace_uid'))],
                                                                    'displayName': [
                                                                        (MODIFY_REPLACE, [kwargs.get('replace_uid')])],
                                                                    'givenName': [
                                                                        (MODIFY_REPLACE, [kwargs.get('replace_uid')])],
                                                                    'homeDirectory': [
                                                                        (MODIFY_REPLACE, ['/home/{}'.format(
                                                                            kwargs.get('replace_uid'))])],
                                                                    'mail': [(MODIFY_REPLACE, [
                                                                        '{}@magicengine.com.cn'.format(
                                                                            kwargs.get('replace_uid'))])]})
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

        # 获取要更改的属性名
        attribute_name = kwargs.get('will_attribute_name')

        # 获取要更爱的属性值
        attribute_value = kwargs.get('attribute_value')

        for name in args:
            dn = "uid={},ou={},{}".format(name.get('uid')[0], ou, self.args.base_dc)
            # 拼接准备更改的字段
            user_mail = "{}{}".format(name.get('uid')[0], kwargs.get('attribute_value'))
            status, result, response, _ = self.conn.modify(dn, {attribute_name: [(MODIFY_REPLACE, user_mail)]})
            ret[name.get('uid')[0]] = result['description']
        return ret

    def __del__(self):
        # 关闭链接
        self.conn.unbind()
