# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-08 14:11
from enum import Enum


class BugType(Enum):
    SQLINJECTION = 'SqlInjection'
    RCE = 'RCE'
    READFILE = 'READ FILE'
    XXE = 'XXE'
    SSRF = 'SSRF'
    DESERIALIZE = 'Deserialize'


class BugLevel(Enum):
    HIGH = 'High'
    MEDIUM = 'Midium'
    LOW = 'Low'
