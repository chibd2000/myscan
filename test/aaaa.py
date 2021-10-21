# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-10-12 13:54

from core.MyGlobalVariableManager import GlobalVariableManager
from test.bbbb import test

if __name__ == '__main__':

    GlobalVariableManager.init()
    GlobalVariableManager.setValue('aa', 111)
    test()