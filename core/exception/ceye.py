# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-12-06 18:15



class DnslogError(Exception):
    """@todo: dnslog Base class"""
    pass

#
# class DnslogPrivilegeError(DnslogError):
#     def __init__(self, message, *args, **kwargs):
#         self.message = message
#

class CeyeError(DnslogError):
    """@todo: Ceye Base class"""
    pass


class CeyePrivilegeError(CeyeError):
    """@todo: Ceye subclass, which result in priviledge error"""
    def __init__(self, message=None, *args, **kwargs):
        self.message = message


class EyesError(DnslogError):
    """@todo: Eyes Base class"""


class EyesPrivilegeError(CeyeError):
    """@todo: Eyes subclass, which result in priviledge error"""
    def __init__(self, message=None, *args, **kwargs):
        self.message = message
