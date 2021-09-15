# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-08 14:11


# About bug 相关的描述枚举类
class BugType:
    SQLINJECTION = 'SQL Injection'
    RCE = 'RCE'
    READFILE = 'READ FILE'
    XXE = 'XXE'
    SSRF = 'SSRF'
    DESERIALIZE = 'Deserialize'
    CODELEAKAGE = 'Code Leakage'
    UPLOADFILE = 'Upload File'
    WRITEFILE = 'Write File'
    UNAUTH = 'UNAUTH'
    BACKUP = 'BACKUP'
    DIRECTORYTRAVERSAL = 'Directory Traversal'
    ANYUSERLOGIN = 'Any User Login'


class BugLevel:
    HIGH = 'High'
    MEDIUM = 'Midium'
    LOW = 'Low'
