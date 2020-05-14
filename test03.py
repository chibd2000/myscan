# coding=utf-8

import subprocess
import os
import re
abs_path = os.getcwd() + os.path.sep


'''他山之石subDomainsdBrute模块'''
def subDomainsdBrute():
    cmd = 'python2 ' + abs_path + 'subDomainsBrute' + os.path.sep + 'subDomainsBrute.py ' + 'nbcc.cn ' + '-i --full'
    res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    result = res.stdout.read().decode()

    fina_res = re.split(r'\s+', result, flags=re.S)
    for i in fina_res:
        if fina_res[fina_res.index(i)] == '':
            fina_res.remove(i)

    res.terminate()
    return fina_res



b = subDomainsdBrute()
print(b)
