# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-29 12:57

import requests
import re

headers = {
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

resp = requests.get(url='https://www.jd.com', headers=headers)
print(resp.content.decode('utf-8'))
mat = re.search(r'©[\s&nbsp;]+(.*)[\s&nbsp;]+版权所有', resp.content.decode('utf-8'))
print(mat)