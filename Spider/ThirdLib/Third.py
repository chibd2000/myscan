# coding=utf-8
import requests
import logging
import json
import time
import re
import asyncio
import aiohttp
from Config.config import *
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.INFO, filemode='a', format="[%(levelname)s]%(asctime)s %(message)s")
requests.packages.urllib3.disable_warnings()


# ske大师兄/oneforall
class ThirdBase(object):
    source = "ThirdBase"

    def __init__(self):
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': 'https://www.google.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'X-Forwarded-For': '127.0.0.1',
        }
        self.resList = []
        self.reqTimeout = 10
