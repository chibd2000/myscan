# coding=utf-8

# from Spider.BaseSpider import *
import nmap
import multiprocessing
import json
from threading import Lock
import openpyxl
import os
import requests
import re
import chardet

abs_path = os.getcwd() + os.path.sep

# 端口扫描的实现
class PortScan(object):
    def __init__(self, domain, _ip):
        self.domain = domain
        self.scanlists = list()
        self.ports = list()
        self.lock = Lock()
        self._ip = _ip

    def test1(self):
        print(self.domain)


if __name__ == '__main__':
    res = list()
    ip_lists = ['120.79.66.58', '116.85.41.113']
    pool = multiprocessing.Pool(5)
    for _ip in ip_lists:
        bbb = PortScan('nbpt.edu.cn', _ip)
        pool.apply_async(func=bbb.test1)
    pool.close()
    pool.join()
