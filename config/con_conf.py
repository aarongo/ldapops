# -*- coding: utf-8 -*-

__author__ = "ModeYl"


_LDAP_HOST = "ldap-server.magic.com"
_LDAP_PORT = 389
_LDAP_USER = "cn=manager,dc=magic,dc=com"
_LDAP_PASSWORD = "root123"
_LDAP_BASE_DC = "dc=magic,dc=com"


def get_config_parameter(parameter):
    if parameter == 'LDAP_HOST':  # String
        return _LDAP_HOST
    elif parameter == 'LDAP_PORT':  # int
        return _LDAP_PORT
    elif parameter == 'LDAP_USER':  # String
        return _LDAP_USER
    elif parameter == 'LDAP_PASSWORD':  # String
        return _LDAP_PASSWORD
    elif parameter == 'LDAP_BASE_DC':  # String
        return _LDAP_BASE_DC
