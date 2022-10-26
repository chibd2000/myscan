# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-23 20:25


class NetGatherError(Exception):
    """@todo: NetGather Base class"""
    pass

class NetPrivilegeError(NetGatherError):
    """@todo: NetGather subclass, which result in priviledge error"""

    def __init__(self, message=None, *args, **kwargs):
        self.message = message

class NetPageLimitError(NetGatherError):
    """@todo: NetGather subclass, which result in search page limit"""

    def __init__(self, message=None, *args, **kwargs):
        self.message = message

class NetSyntaxError(NetGatherError):
    """@todo: NetGather subclass, which result in search syntax incorrect"""

    def __init__(self, message=None, *args, **kwargs):
        self.message = message

class NetTokenError(NetGatherError):
    """@todo: NetGather subclass, which result in unauth search"""

    def __init__(self, message=None, *args, **kwargs):
        self.message = message
