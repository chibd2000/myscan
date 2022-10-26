# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-08 14:11


# About bug 相关的描述枚举类
class BugType:
    SQLINJECTION = 'SQL Injection'
    RCE = 'Remote Code Execution'
    READFILE = 'Read File'
    XXE = 'XXE'
    SSRF = 'SSRF'
    DESERIALIZE = 'Deserialize'
    UPLOADFILE = 'Upload File'
    WRITEFILE = 'Write File'
    UNAUTH = 'Unauth'
    BACKUP = 'Backup'
    DIRECTORYTRAVERSAL = 'Directory Traversal'
    ANYUSERLOGIN = 'Any User Login'
    BYPASSPERMISSION = 'Bypass Permission'
    SENSITIVE = 'Sensitive'
    FINGER = 'Finger'
    MISCONFIGURATION = 'Misconfiguration'
    BLAST = 'Blast'


class BugLevel:
    HIGH = 'High'
    MEDIUM = 'Midium'
    LOW = 'Low'
