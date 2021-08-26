# coding=utf-8

from Common.common import *
import openpyxl
import requests
import abc
import re
import chardet
import logging
import time
import random
import base64
from threading import Lock

requests.packages.urllib3.disable_warnings()
logging.basicConfig(level=logging.INFO, filemode='a', format="[%(levelname)s]%(asctime)s %(message)s")
# filename='./Logs/worklog.txt'


class Spider(metaclass=abc.ABCMeta):
    source = "spider"

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/55.0.2883.75 Safari/537.36"}
        self.lock = Lock()
        self.reqTimeout = 10
        self.resList = []

    @abc.abstractmethod
    def write_file(self, web_lists, target, page):
        pass

    @abc.abstractmethod
    def spider(self):
        pass

    @abc.abstractmethod
    def main(self):
        pass

    # 获取 title service
    def get_titleAndservice(self, link, port=''):
        if port == 443:
            link = 'https://{}'.format(link)

        if 'http' not in link:
            if port != '':
                link = 'http://{}:{}'.format(link, str(port))
            else:
                link = 'http://{}'.format(link)
        try:
            resp = requests.get(link, timeout=3, verify=False)
            detectencode = chardet.detect(resp.content)  # 利用chardet模块检测编码
            title = re.findall(r'<title>(.*?)</title>', resp.content.decode(detectencode["encoding"]), re.S)[0].strip(
                ' ').strip('\r\n').strip('\n').strip('\r')
        except:
            title = ''
        try:
            service = resp.headers.get('Server')
        except:
            service = ''
        try:
            content = resp.text
        except:
            content = ''
        return title, service, content

    # 匹配每个页面中的子域名
    def matchSubdomain(self, domain, text):
        regexp = r'(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.){0,}' + domain.replace('.', r'\.')
        result = re.findall(regexp, text, flags=re.I | re.S)
        if not result:
            return list()
        deal = map(lambda s: s.lower(), result)
        return list(deal)
