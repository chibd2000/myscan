# coding=utf-8
import re


class BaseThird(object):
    __slots__ = ('source', 'headers', 'reqTimeout', 'domain', 'resList')

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
        self.source = "BaseThird"
        self.domain = ''

    # 匹配每个页面中的子域名
    def matchSubdomain(self, domain, text):
        regexp = r'(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.){0,}' + domain.replace('.', r'\.')
        result = re.findall(regexp, text, flags=re.I | re.S)
        if not result:
            return list()
        deal = map(lambda s: s.lower(), result)
        return list(deal)
