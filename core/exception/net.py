# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-23 20:25


class NetGatherError(Exception):
    """空间搜索引擎异常Base类"""
    pass


class NetPrivilegeError(NetGatherError):
    """空间搜索引擎特权问题导致的异常封装类"""
    def __init__(self, message):
        self.message = message


class NetPageLimitError(NetGatherError):
    """空间搜索引擎页数问题导致的异常封装类"""
    def __init__(self, message):
        self.message = message
