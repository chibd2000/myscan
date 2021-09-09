# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 20:48

class Mydict(dict):
    def __getattr__(self, item):
        pass
