# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-27 1:06

"""
@todo: prepare for github error, write in 2021.11.27 1.06 @zpchcbd
"""


class GithubSearchError(Exception):
    """@todo: GithubSearch Base class"""
    pass


class GithubPrivilegeError(GithubSearchError):
    """@todo: GithubSearch subclass, which result in priviledge error"""
    def __init__(self, message=None, *args, **kwargs):
        self.message = message
