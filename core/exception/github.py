# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-27 1:06

"""
prepare for github error, write in 2021.11.27 1.06 @zpchcbd
"""


class GithubSearchError(Exception):
    """GithubSearch异常Base类"""
    pass


class GithubPrivilegeError(GithubSearchError):
    """GithubSearch权限问题导致的异常封装类"""

    def __init__(self, message):
        self.message = message
