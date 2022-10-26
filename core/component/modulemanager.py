# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-10 1:06

from core.data import path_dict
from core.component.moduleloader import ModuleLoader
from core.component.variablemanager import GlobalVariableManager
from prettytable import PrettyTable
import os
import re
import importlib


class ModuleManager(object):
    """prepare exploit, saving time for multi save module in cmsExploit. write in 2021.9.10 @zpchcbd"""
    remainModuleList = []
    _registerSameTypeMultiModuleList = []

    def __init__(self):
        self.module_loader = ModuleLoader()
        # self.init_multi_module_dict(moduleType)

    # 减少同类型多模块加载的时间消耗所写的类
    def init_multi_module_dict(self, module_type):
        if module_type == 'exploit':
            exploit_rule = {}
            for parent, dirnames, filename_list in os.walk(path_dict.EXPLOIT_PATH, followlinks=True):
                dir_file_length = 0
                for filename in filename_list:
                    if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py' or filename[-3:] != '.py':
                        continue
                    dir_file_length += 1
                if dir_file_length >= 1:
                    dir_name = re.split('[\\\\/]', parent)[-1]
                    exploit_rule[dir_name] = []
            GlobalVariableManager.setValue('exploitRule', exploit_rule)

    @staticmethod
    def show_module():
        '''
        show module name and path
        @return: void
        '''
        file_length = 0
        module_table = PrettyTable(['漏洞', '漏洞类型', '漏洞编号', '漏洞等级', '漏洞来源', '漏洞信息'], title='explot module table')
        for parent, dirnames, filenameList in os.walk(path_dict.EXPLOIT_PATH, followlinks=True):
            for filename in filenameList:
                if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py' or filename[-3:] != '.py':
                    continue
                file_length += 1
                file_path = os.path.join(parent, filename)
                _python_module_object = importlib.import_module('.'.join(re.split('[\\\\/]', file_path[len(path_dict.ROOT_PATH):-3])))
                _script_module = getattr(_python_module_object, 'Script')
                _script_path = '.'.join(re.split('[\\\\/]', file_path[len(path_dict.ROOT_PATH):-3]))
                script_module_information = _script_module(None).print()
                module_table.add_row([_script_path, script_module_information[0], script_module_information[1], script_module_information[2], script_module_information[3], script_module_information[4]])
        print(module_table)

    def find_module(self, keyword):
        '''
        find specific module name and path
        @param keyword: specific keyword from exploit module
        @return: void
        '''
        file_length = 0
        module_table = PrettyTable(['漏洞', '漏洞类型', '漏洞编号', '漏洞等级', '漏洞来源', '漏洞信息'], title='explot module table')
        for parent, dirnames, filenameList in os.walk(path_dict.EXPLOIT_PATH, followlinks=True):
            for filename in filenameList:
                if filename[-3:] == 'pyc' or filename[:2] == '__' or filename[-5:] == '__.py' or filename[-3:] != '.py':
                    continue
                file_length += 1
                file_path = os.path.join(parent, filename)
                _python_module_object = importlib.import_module('.'.join(re.split('[\\\\/]', file_path[len(path_dict.ROOT_PATH):-3])))
                _script_module = getattr(_python_module_object, 'Script')
                _script_path = '.'.join(re.split('[\\\\/]', file_path[len(path_dict.ROOT_PATH):-3]))
                if keyword in _script_path.lower():
                    script_module_information = _script_module(None).print()
                    module_table.add_row([_script_path, script_module_information[0], script_module_information[1], script_module_information[2], script_module_information[3], script_module_information[4]])
        print(module_table)

    def load_module(self, module_type, module_object=None):
        '''

        @param module_type:
        @param module_object:
        @return:
        '''
        self.module_loader.module_load(module_type, module_object)

    def get_load_module_list(self):
        '''

        @return:  module_loader -> module_load() -> module_list
        '''
        return self.module_loader.module_list


if __name__ == '__main__':
    pass
    # mm = ModuleManager('exploit')
    # mm.checkModule()
