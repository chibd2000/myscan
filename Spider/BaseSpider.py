# coding=utf-8

from Spider.Common.common import *
import requests
import re
import chardet
import logging
from threading import Lock
import openpyxl
requests.packages.urllib3.disable_warnings()
logging.basicConfig(level=logging.INFO, format="[%(levelname)s]%(asctime)s %(message)s")


'''爬取基类'''
class Spider(object):

    def __init__(self):
        self.source = 'BaseSpider'  #
        self.lock = Lock()
        self.header = {}
        self.target = ''  # 被爬取的域名

    #  写文件函数
    def write_file(self, web_lists, target, page):
        pass

    # 爬取函数
    def spider(self):
        pass

    #  启动函数
    def main(self):
        pass

    # 获取 title service
    def get_titleAndservice(self, link, port=''):
        if port == 443:
            link = 'https://' + link
        if 'http' not in link:
            link = 'http://' + link
        try:
            resp = requests.get(link, timeout=3, verify=False)
            detectencode = chardet.detect(resp.content)  # 利用chardet模块检测编码
            title = re.findall(r'<title>(.*?)</title>', resp.content.decode(detectencode["encoding"]), re.S)[0].strip(' ').strip('\r\n').strip('\n').strip('\r')
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

    # 匹配文本中的子域名
    def matchSubdomain(self, domain, text):
        regexp = r'(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.){0,}' + domain.replace('.', r'\.')
        result = re.findall(regexp, text, flags=re.I | re.S)
        if not result:
            return list()
        deal = map(lambda s: s.lower(), result)
        return list(deal)
