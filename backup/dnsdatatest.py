# coding=utf-8
from Spider.DnsDataSpider import *

class a(object):

    def __init__(self):
        self.task_list = list()

    def dnsspider(self):
        dnsdatalist = DnsDataSpider('nbcc.cn').main()
        return dnsdatalist

    def run(self):
        self.task_list = self.dnsspider()
        print(self.task_list)


if __name__ == '__main__':
    print(a().dnsspider())
