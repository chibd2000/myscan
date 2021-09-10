# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-08 14:11
from enum import Enum


# About bug 相关的描述枚举类
class BugType(Enum):
    SQLINJECTION = 'SQL Injection'
    RCE = 'RCE'
    READFILE = 'READ FILE'
    XXE = 'XXE'
    SSRF = 'SSRF'
    DESERIALIZE = 'Deserialize'
    CODELEAKAGE = 'Code Leakage'
    UPLOADFILE = 'Upload File'


class BugLevel(Enum):
    HIGH = 'High'
    MEDIUM = 'Midium'
    LOW = 'Low'