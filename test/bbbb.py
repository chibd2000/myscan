# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-10-12 13:54

from core.MyGlobalVariableManager import GlobalVariableManager

def test():
    a = GlobalVariableManager.getValue('aa')

    print(a)