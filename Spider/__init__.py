# coding=utf-8
from spider.public import *


class BaseSpider(metaclass=abc.ABCMeta):
    __slots__ = ('source', 'headers', 'reqTimeout', 'domain', 'resList')

    def __init__(self):
        self.source = 'BaseSpider'
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
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
        self.reqTimeout = 10
        self.resList = []

    @abc.abstractmethod
    def writeFile(self, web_lists, page):
        pass

    @abc.abstractmethod
    def spider(self):
        pass

    @abc.abstractmethod
    def main(self):
        pass

    # 获取 title service
    async def getTitleAndService(self, session, link):
        try:
            async with session.get(url=link, headers=self.headers,
                                   verify_ssl=False,
                                   timeout=10) as response:
                text = await response.text()
                title = re.findall(r'<title>(.*?)</title>', text, re.S)[0].strip(
                    ' ').strip('\r\n').strip('\n').strip('\r')
            try:
                service = response.headers.get('Server')
            except:
                service = ''
            try:
                content = text
            except:
                content = ''
            return title, service, content
        except:
            title = ''
            return title, '', ''

    # 获取 title service
    def getTitleAndService2(self, link, port):
        try:
            resp = requests.get(url=link, verify=False)
            text = resp.content.decode('utf-8')
            title = re.findall(r'<title>(.*?)</title>', text, re.S)[0].strip(
                ' ').strip('\r\n').strip('\n').strip('\r')
            try:
                service = resp.headers.get('Server')
            except:
                service = ''
            try:
                content = text
            except:
                content = ''
            return title, service, content
        except:
            title = ''
            return title, '', ''

    # 匹配每个页面中的子域名
    def matchSubdomain(self, domain, text):
        regexp = r'(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.){0,}' + domain.replace('.', r'\.')
        result = re.findall(regexp, text, flags=re.I | re.S)
        if not result:
            return list()
        deal = map(lambda s: s.lower(), result)
        return list(deal)
