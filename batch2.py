# coding=utf-8

from Spider.BaiduSpider import *
from Spider.CtfrSpider import *
from Spider.NetSpider import *
from Spider.DnsBruteSpider import *
from Spider.DnsDataSpider import *
from Spider.PortSpider import *
from Spider.Common import resolve
from Exploit.IpUnauthExploit import *
from Exploit.HttpUnauthExploit import *
from Exploit.CmsExploit import *
from Exploit.SensitiveExploit import *
from ThridLib.virustotal import *
from threading import Thread, Lock



import os
import argparse
import time
import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

abs_path = os.getcwd() + os.path.sep


'''信息搜集类'''
class Spider(object):
    def __init__(self, domain):
        self.domain = domain  # 要爬取的域名
        self.thread_list = list()  # 线程启动列表
        self.task_list = list()  # 用来存储所有匹配到的域名
        self.clear_task_list = list()  # 存储整理过后的域名 [{"subdomain": "www.ncist.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        self.lock = Lock()

    '''dns数据库查询'''
    def dnsspider(self):
        dnsdatalist = DnsDataSpider(self.domain).main()
        self.lock.acquire()
        self.task_list.extend(dnsdatalist)
        self.lock.release()

    '''程序的入口点'''
    def run(self):
        self.dnsspider()


if __name__ == '__main__':
    domain = 'nbcc.cn'

    # 测试搜集域名跑完的时间
    spider = Spider(domain)


    clear_task_list = spider.run()


