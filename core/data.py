# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-14 22:56

from core.component.customdict import AttributeDict
from core.component.variablemanager import GlobalVariableManager

path_dict = AttributeDict()  # 初始化相关路径信息
config_dict = AttributeDict()  # 初始化相关配置信息

try:
    from core.logger import Logger
    gLogger = Logger()
except:
    print('[-] logger init fail.')
    # exit(0)
