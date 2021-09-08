# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-07 16:47

import importlib
import os
import re
# import sys
abs_path = os.getcwd() + os.path.sep  # 路径


# exp loader, study for python
class ModuleLoader(object):
    def __init__(self, modulePath, object):
        self.moduleList = []
        self.modulePath = modulePath  # 'exploit/web'
        self.object = object

    def __moduleLoad(self, module=None, type=None):
        try:
            if module is None:
                # default
                # 因为分目录了，所以这里想要动态加载模块只能是os.walk()
                # sys.path.append(self.modulePath)
                if type == 'third':
                    pass
                elif type == 'exploit':
                    for a, dirnames, filenameList in os.walk(self.modulePath, followlinks=True):
                        for filename in filenameList:
                            if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py':
                                continue
                            try:
                                filePath = os.path.join(a, filename)
                                module = importlib.import_module('.'.join(re.split('[\\\\/]', filePath[len(abs_path):-3])))
                                # module = importlib.import_module('FineReport')
                                if hasattr(module, self.object):
                                    aModule = getattr(module, self.object)
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
            elif isinstance(module, str):
                pass
            elif isinstance(module, list):
                pass
            else:
                pass
        except ModuleNotFoundError as e:
            print('module not found, {}'.format(e.__str__()))

    # for single 单个测试
    def singleModuleLoad(self, module: str):
        return self.__moduleLoad(module, type=None)

    # for twp/three poc exp 加载>2
    def multiModuleLoad(self, module: str):
        return self.__moduleLoad(module, type=None)

    # default, all module 加载所有的
    def defaultModuleLoad(self, type):
        return self.__moduleLoad(module=None, type=type)


if __name__ == '__main__':
    moduleloader = ModuleLoader('exploit\\web\\', 'Script')
    moduleloader.defaultModuleLoad(type='exploit')
