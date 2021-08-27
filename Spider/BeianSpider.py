# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 13:46
from spider.BaseSpider import *

from lxml import etree


class BeianSpider(Spider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'Beian'
        self.domain = domain

    def write_file(self, web_lists, target, page):
        pass

    def spider(self):
        def chinaz(url):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel cai) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
            url = f'https://icp.chinaz.com/home/info?host={url}'

            try:
                response = requests.get(url=url, headers=headers)
                html = etree.HTML(response.text)
                url_href = html.xpath('//div[@class="siteInfo"]/p/text()')
                if not url_href[0].startswith('--'):
                    urls = url_href[2:]
                    print(urls)
            except Exception as e:
                print(e)

    def main(self):
        pass


if __name__ == '__main__':
    BeianSpider("geely.com")
