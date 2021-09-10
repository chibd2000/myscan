# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-07 16:47

import importlib
import os
import re
from core.MyConstant import ModulePath

# import sys
abs_path = os.getcwd() + os.path.sep  # 路径


# exp loader, study for python
class ModuleLoader(object):
    def __init__(self):
        self.moduleList = []

    @staticmethod
    def showModule(moduleType='exploit'):
        def showExploitModule():
            fileLength = 0
            for parent, dirnames, filenameList in os.walk(abs_path + ModulePath.EXPLOIT, followlinks=True):
                for filename in filenameList:
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py':
                        continue
                    fileLength += 1
                    filePath = os.path.join(parent, filename)
                    print('.'.join(re.split('[\\\\/]', filePath[len(abs_path):-3])))
            print('[+] exploit module size: {}'.format(fileLength))

        def showThirdModule():
            fileLength = 0
            for parent, dirnames, filenameList in os.walk(abs_path + ModulePath.THIRDLIB, followlinks=True):
                for filename in filenameList:
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py':
                        continue
                    fileLength += 1
                    filePath = os.path.join(parent, filename)
                    print('.'.join(re.split('[\\\\/]', filePath[len(abs_path):-3])))
            print('[+] third module size: {}'.format(fileLength))

        if moduleType == 'all':
            showThirdModule()
            print('=======================================')
            showExploitModule()
        elif moduleType == 'exploit':
            showExploitModule()
        elif moduleType == 'third':
            showThirdModule()
        else:
            pass

    def moduleLoad(self, moduleType, module=None):
        try:
            if module is None:
                return self._defaultModuleLoad(moduleType=moduleType)  # moduleType: third | exploit
            elif isinstance(module, str):
                return self._singleModuleLoad(
                    module=module)  # single module load, for example exploit.web.v2Conference.sql_inject
            elif isinstance(module, list):
                return self._multiModuleLoad(module=module)  # multi module load, for example exploit.web.v2Conference.sql_inject,
            else:
                pass
        except ModuleNotFoundError as e:
            print('module not found, {}'.format(e.__str__()))

    # 后面的用于单个payload检测，要不然每次都需要写个py文件来跑，太麻烦
    # for single 单个测试
    def _singleModuleLoad(self, module: str):
        try:
            modulePY = importlib.import_module(module)
            if hasattr(modulePY, 'Script'):
                aModule = getattr(modulePY, 'Script')
                self.moduleList.append(aModule)
        except Exception as e:
            print('import module {} error, {}'.format(module, e.__str__()))
        return self.moduleList

    # for twp/three poc exp 加载>2
    def _multiModuleLoad(self, moduleList: list):
        for modulePackage in moduleList:
            try:
                modulePY = importlib.import_module(modulePackage)
                if hasattr(modulePY, 'Script'):
                    aModule = getattr(modulePY, 'Script')
                    self.moduleList.append(aModule)
            except Exception as e:
                print('import module {} error, {}'.format(modulePackage, e.__str__()))
        return self.moduleList

    # default, all module 加载所有的
    def _defaultModuleLoad(self, moduleType):
        # default
        # 因为分目录了，所以这里想要动态加载模块只能是os.walk()
        # sys.path.append(self.modulePath)
        if moduleType == 'third':
            for parent, dirnames, filenameList in os.walk(abs_path + ModulePath.THIRDLIB, followlinks=True):
                for filename in filenameList:
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py':
                        continue
                    try:
                        filePath = os.path.join(parent, filename)
                        modulePY = importlib.import_module(
                            '.'.join(re.split('[\\\\/]', filePath[len(abs_path):-3])))
                        # module = importlib.import_module('FineReport')
                        if hasattr(modulePY, 'do'):
                            aModule = getattr(modulePY, 'do')
                            self.moduleList.append(aModule)
                    except Exception as e:
                        print('import module {} error, {}'.format(filename, e.__str__()))
        elif moduleType == 'exploit':
            for parent, dirnames, filenameList in os.walk(abs_path + ModulePath.EXPLOIT, followlinks=True):
                for filename in filenameList:
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py':
                        continue
                    try:
                        filePath = os.path.join(parent, filename)
                        modulePY = importlib.import_module(
                            '.'.join(re.split('[\\\\/]', filePath[len(abs_path):-3])))
                        # module = importlib.import_module('FineReport')
                        if hasattr(modulePY, 'Script'):
                            aModule = getattr(modulePY, 'Script')
                            self.moduleList.append(aModule)
                    except Exception as e:
                        print('import module {} error, {}'.format(filename, e.__str__()))
        # modules = filter(lambda x: (True, False)[x[-3:] == 'pyc' or x[-5:] == '__.py' or x[:2] == '__'],
        #                  os.listdir(self.modulePath))
        # for _ in modules:
        #     print(_)
        #     module = importlib.import_module(_[:-3])
        #     if hasattr(module, 'Script'):
        #         aClass = getattr(module, self.object)
        #         print(aClass)
        return self.moduleList


if __name__ == '__main__':
    moduleloader = ModuleLoader()
    moduleloader.moduleLoad(moduleType='exploit', module='*')
