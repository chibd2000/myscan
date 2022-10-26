# coding=utf-8
# @Author   : zpchcbd HG team
# @blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-11-26 18:48

"""如果之后继续进行数据库整理的话，再把这个写上 created in 2021.11.26 18.54 @zpchcbd"""
import sqlite3


class Database:
    database_path = ''

    def __init__(self, database_path=None):
        self.database_path = self.database_path if database_path is None else database_path
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = sqlite3.Connection(self.database_path)
            self.cursor = self.connection.cursor()
        except sqlite3.DatabaseError:
            pass
        except sqlite3.Error:
            pass

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def execute(self):
        pass


class TaskDB(Database):
    def __init__(self, database_path):
        super().__init__(database_path)

    def insert(self):
        pass

    def delete(self):
        pass

    def update(self):
        pass

    def select(self):
        pass
