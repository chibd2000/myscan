# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-10-12 13:58


"""
aaaa.py

from core.MyGlobalVariableManager import GlobalVariableManager
from test.bbbb import test

GlobalVariableManager.init()
GlobalVariableManager.setValue('aa', 111)
test()
----------------
bbbb.py

from core.MyGlobalVariableManager import GlobalVariableManager

def test():
    a = GlobalVariableManager.getValue('aa')
    print(a)
"""


class GlobalVariableManager:
    @staticmethod
    def init():
        # 初始化
        global _global_dict
        _global_dict = {}

    @staticmethod
    def setValue(key, value):
        # 定义一个全局变量
        _global_dict[key] = value

    @staticmethod
    def getValue(key, defValue=None):
        # 获得一个指定的全局变量, 不存在则返回默认值
        try:
            return _global_dict[key]
        except KeyError:
            return defValue
