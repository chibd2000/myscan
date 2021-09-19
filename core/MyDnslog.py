# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 21:44

import requests
import time


class Dnslog(object):
    __slots__ = ('token', 'session', 'domain')

    def __init__(self):
        self.token = ''
        self.session = ''
        self.domain = ''
        self.init()

    def _getCookie(self):

        session = requests.session()
        self.session = session
        resp = session.get('http://dnslog.cn/getdomain.php?t=0.4503404253301704')
        self.domain = resp.text
        print(self.domain)
        time.sleep(5)

    def init(self):
        self._getCookie()

    def getRecords(self):
        resp = self.session.get('http://dnslog.cn/getrecords.php?t=0.7209060121871593')
        print("================")
        print(resp.text)


if __name__ == '__main__':
    dnslog = Dnslog()
    dnslog.init()
    dnslog.getRecords()
