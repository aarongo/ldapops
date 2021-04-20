# -*- coding: utf-8 -*-

from ldap3.utils.hashed import hashed
from ldap3 import HASHED_SALTED_SHA
import random


def general_user_passwd(password):
    """
    生成用户密码
    :param password: str
    :return: 加密后的用户密码: 使用 ssha 形式
    """

    ret = hashed(HASHED_SALTED_SHA, password)

    return ret


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
    :param args: LDAP 返回的信息--LIST
    :param kwargs: 准备创建的组信息--Dict
    :return: Boolean
    """

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
