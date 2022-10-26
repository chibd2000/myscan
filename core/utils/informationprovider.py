# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 20:31
from core.data import path_dict
import os


class InformationProvider(object):
    file_type = 'r'

    @staticmethod
    def read_file(filename):
        filename_path = os.path.join(path_dict.DICT_PATH, filename)
        if os.path.isfile(filename_path):
            try:
                with open(filename_path, InformationProvider.file_type) as f:
                    return f.readlines()
            except FileNotFoundError as e:
                print('InformationProvider file not found, {}'.format(e.__str__()))
        return None

    @staticmethod
    def read_dict_file(filename):
        if os.path.isfile(filename):
            try:
                with open(filename, InformationProvider.file_type) as f:
                    return f.read()
            except FileNotFoundError as e:
                print('InformationProvider file not found, {}'.format(e.__str__()))
        return None

    @staticmethod
    def generate(username_list, password_list):
        username_list = list(set(username_list))
        password_list = list(set(password_list))
        for username in username_list:
            username = username.replace('\r', '').replace('\n', '').strip().rstrip()
            for password in password_list:
                if '%user%' not in password:
                    password = password
                else:
                    password = password.replace("%user%", username)
                password = password.replace('\r', '').replace('\n', '').strip().rstrip()
                yield username, password

                # 首位大写也爆破下，再看，每次套接字时间花费太多
                # if len(password) > 2:
                #     password2 = password[0].upper() + password[1:]
                #     if password2 != password:
                #         yield username, password2
