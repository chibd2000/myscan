# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2020-11-23 20:45
from core.public import *
from core.data import path_dict
from core.init import parser_init, path_init, global_variable_init, config_init
from core.go import start

version = sys.version.split()[0]
if version < "3":
    exit("[-] Incompatible Python version detected ('%s'). For successfully running program you'll have to use version 3  (visit 'http://www.python.org/download/')" % version)

if __name__ == '__main__':
    start_time = time.time()
    parser = parser_init()
    path_dict.ROOT_PATH = os.getcwd() + os.path.sep
    path_init()
    config_init()
    global_variable_init()
    start(parser)
