# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 20:31


import os


class InformationProvider(object):
    fileType = 'r'
    # dictPath = 'dict/information'
    dictPath = r'D:/ALL/myscan/dict/information'

    @staticmethod
    def readFile(filename):
        if os.path.isfile(filename):
            with open(filename, InformationProvider.fileType) as f:
                return f.readlines()
        return None

    @staticmethod
    def generate(usernameList, passwordList):
        usernameList = list(set(usernameList))
        passwordList = list(set(passwordList))
        for username in usernameList:
            username = username.replace('\r', '').replace('\n', '').strip().rstrip()
            for password in passwordList:
                if '%user%' not in password:
                    password = password
                else:
                    password = password.replace("%user%", username)
                password = password.replace('\r', '').replace('\n', '').strip().rstrip()
                yield username, password

                # 首位大写也爆破下
                if len(password) > 2:
                    password2 = password[0].upper() + password[1:]
                    if password2 != password:
                        yield username, password2

    @staticmethod
    def getRedisInfor():
        pass

    @staticmethod
    def getMysqlInfor():
        pass

    @staticmethod
    def getMongodbInfor():
        pass

    @staticmethod
    def getRdpInfor():
        pass

    @staticmethod
    def getRsyncInfor():
        pass

    @staticmethod
    def getMssqlInfor():
        pass

    @staticmethod
    def getMysqXlInfor():
        pass

    @staticmethod
    def getXXXXInfor():
        pass

    @staticmethod
    def getXXXInfor():
        pass
