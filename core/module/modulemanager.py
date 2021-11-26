# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-10 1:06

from core.constant import ModulePath
from core.module.moduleloader import ModuleLoader
from core.variablemanager import GlobalVariableManager
import inspect
import importlib
import os
import re

abs_path = os.getcwd() + os.path.sep  # 路径


class ModuleManager(object):
    """prepare exploit, saving time for multi save module in cmsExploit. write in 2021.9.10 @zpchcbd"""
    remainModuleList = []
    _registerSameTypeMultiModuleList = []

    def __init__(self, moduleType):
        self.moduleLoader = ModuleLoader(moduleType)
        self.initMultiModuleDict(moduleType)

    def getSameTypeMultiModules(self, sameTypeMultiModuleName):
        moduleName = sameTypeMultiModuleName
        destinationList = GlobalVariableManager.getValue(sameTypeMultiModuleName)
        """
        返回全局变量中保存的同类型多模块的目录下的所有模块
        """

    # 减少同类型多模块加载的时间消耗所写的类
    def initMultiModuleDict(self, moduleType):
        if moduleType == 'exploit':
            exploitRule = {}
            for parent, dirnames, filenameList in os.walk(abs_path + ModulePath.EXPLOIT, followlinks=True):
                dirFileLength = 0
                for filename in filenameList:
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py' or filename[-3:] != '.py':
                        continue
                    dirFileLength += 1

                if dirFileLength >= 2:
                    dirName = re.split('[\\\\/]', parent)[-1]
                    exploitRule[dirName] = []
            GlobalVariableManager.setValue('exploitRule', exploitRule)

    @staticmethod
    def showModule(moduleType='exploit'):
        def showExploitModule():
            fileLength = 0
            for parent, dirnames, filenameList in os.walk(abs_path + ModulePath.EXPLOIT, followlinks=True):
                for filename in filenameList:
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py' or filename[-3:] != '.py':
                        continue
                    fileLength += 1
                    filePath = os.path.join(parent, filename)
                    print('.'.join(re.split('[\\\\/]', filePath[len(abs_path):-3])))
            print('[+] exploit module size: {}'.format(fileLength))

        def showThirdModule():
            fileLength = 0
            for parent, dirnames, filenameList in os.walk(abs_path + ModulePath.THIRDLIB, followlinks=True):
                for filename in filenameList:
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py' or filename[-3:] != '.py':
                        continue
                    fileLength += 1
                    filePath = os.path.join(parent, filename)
                    print('.'.join(re.split('[\\\\/]', filePath[len(abs_path):-3])))
            print('[+] third module size: {}'.format(fileLength))

        if moduleType == 'all':
            showThirdModule()
            print('=' * 50)
            showExploitModule()
        elif moduleType == 'exploit':
            showExploitModule()
        elif moduleType == 'third':
            showThirdModule()

    def checkModule(self, moduleObject):
        for remainModule in ModuleManager.remainModuleList:
            if moduleObject.name == remainModule['name']:
                pass


# 1、获取Script所有的模块的路径
# 2、最后一个 '.' 之前的相同，那么则表示为 同类型多模块
# 3、如果是同类型多模块的话，那么则随机取其中的一个模块进行利用
def multiScript(scriptObject):
    lines = inspect.stack(context=2)[1].code_context
    decoratedFlag = any(line.startswith('@') for line in lines)
    if decoratedFlag:
        ModuleManager.remainModuleList.append({scriptObject.name: []})
    return scriptObject


@multiScript
class Script:
    name = 'apache'


@multiScript
class Script:
    name = 'apache'


@multiScript
class Script:
    name = 'apache'


if __name__ == '__main__':
    mm = ModuleManager('exploit')
    mm.checkModule()
