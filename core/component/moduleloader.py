# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-07 16:47

from core.data import path_dict, gLogger
import importlib
import os
import re
import traceback

# 模块加载类，用于加载poc用的，相当于一个模块Manager，写这个是用到后面出现新POC检测配合fofa来进行使用，这样会比较方便处理
# exp loader, study for python


class ModuleLoader(object):
    def __init__(self):
        self.module_list = []
        self.load_poc_num = 0

    def module_load(self, module_type, module_object=None):
        try:
            if module_object is None:
                self._default_module_load(module_type)  # moduleType: third | exploit | service
            elif isinstance(module_object, str) and ',' not in module_object and module_object[-1] == '*':
                self.wildcard_module_load(module_object)
            elif isinstance(module_object, str) and ',' not in module_object:
                self._single_module_load(module_object)  # single module load, for example exploit.scripts.a.b
            elif isinstance(module_object, str) and ',' in module_object and '*' in module_object:
                module_object_list = module_object.split(',')
                for module in module_object_list:
                    if '*' not in module:
                        self._single_module_load(module)
                    else:
                        self.wildcard_module_load(module)
            elif isinstance(module_object, str) and ',' in module_object:
                module_object_list = module_object.split(',')
                module_list = [module for module in module_object_list]
                self._multi_module_load(module_list)  # multi module load, for example exploit.scripts.a.b, exploit.scripts.a.c
            gLogger.myscan_debug('load module have %s' % str(self.module_list))
            return self.module_list
        except ModuleNotFoundError as e:
            gLogger.myscan_error('module load error, the error is {}'.format(e.args))
            exit(0)
        except Exception as e:
            error_smg = traceback.format_exc()
            gLogger.myscan_error(error_smg)
            exit(0)

    def wildcard_module_load(self, module: str):
        # again verify
        if module[-1] == '*' and module[-2] == '.':
            load_module_path = module[:-2]
            for parent, dir_names, filename_list in os.walk(path_dict.EXPLOIT_PATH, followlinks=True):
                for filename in filename_list:
                    file_path = os.path.join(parent, filename)
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py' or filename[-3:] != '.py':
                        continue
                    format_poc_file_path = '.'.join(re.split('[\\\\/]', file_path[len(path_dict.ROOT_PATH):-3]))
                    if load_module_path in format_poc_file_path:
                        python_module_object = importlib.import_module(format_poc_file_path)
                        if hasattr(python_module_object, 'Script'):
                            a_module = getattr(python_module_object, 'Script')
                            self.module_list.append(a_module)
                            self.load_poc_num += 1

    # 后面的用于单个payload检测，要不然每次都需要写个py文件来跑，太麻烦
    # for single 单个测试
    def _single_module_load(self, module: str):
        python_module_object = importlib.import_module(module)
        if hasattr(python_module_object, 'Script'):
            a_module = getattr(python_module_object, 'Script')
            self.module_list.append(a_module)
            self.load_poc_num += 1

    # for twp/three poc exp 加载>2
    def _multi_module_load(self, module_list: list):
        for module in module_list:
            python_module_object = importlib.import_module(module)
            if hasattr(python_module_object, 'Script'):
                a_module = getattr(python_module_object, 'Script')
                self.module_list.append(a_module)
                self.load_poc_num += 1

    # default, all module 加载所有的
    def _default_module_load(self, module_type):
        if module_type == 'exploit':
            for parent, dir_names, filename_list in os.walk(path_dict.EXPLOIT_PATH, followlinks=True):
                priority_flag = 0
                for filename in filename_list:
                    if len(filename_list) > 2:
                        for _ in filename_list:
                            _file_path = os.path.join(parent, _)
                            if _[-3:] == 'pyc' or _[:2] == '__' or _[-5:] == '__.py' or _[-3:] != '.py':
                                continue
                            _python_module_object = importlib.import_module('.'.join(re.split('[\\\\/]', _file_path[len(path_dict.ROOT_PATH):-3])))
                            if hasattr(_python_module_object, 'Script'):
                                _script_module = getattr(_python_module_object, 'Script')
                                if _script_module(None).priority == 1:
                                    self.module_list.append(_script_module)
                                    self.load_poc_num += 1
                                    priority_flag = 1
                                    break
                    else:
                        file_path = os.path.join(parent, filename)
                        if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py' or filename[-3:] != '.py':
                            continue
                        python_module_object = importlib.import_module('.'.join(re.split('[\\\\/]', file_path[len(path_dict.ROOT_PATH):-3])))
                        if hasattr(python_module_object, 'Script'):
                            script_module = getattr(python_module_object, 'Script')
                            self.module_list.append(script_module)
                            self.load_poc_num += 1
                    if priority_flag:
                        break

        elif module_type == 'third':
            for parent, dirnames, filenameList in os.walk(path_dict.SPIDER_THIRD_PATH, followlinks=True):
                for filename in filenameList:
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py' or filename[-3:] != '.py':
                        continue
                    file_path = os.path.join(parent, filename)
                    python_module_object = importlib.import_module('.'.join(re.split('[\\\\/]', file_path[len(path_dict.ROOT_PATH):-3])))
                    if hasattr(python_module_object, 'do'):
                        a_module = getattr(python_module_object, 'do')
                        self.module_list.append(a_module)


if __name__ == '__main__':
    moduleloader = ModuleLoader()
    moduleloader.module_load('exploit')
