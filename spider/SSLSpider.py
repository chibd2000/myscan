# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 22:23

from spider.public import *
from spider import BaseSpider


# @keefe @hangniu @ske
class SSLSpider(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'SSLSpider'  # module name
        self.domain = domain
        self.webList = []

    def writeFile(self, web_lists, page):
        try:
            pass
        except Exception as e:
            print('[-] [{}] writeFile error, error is {}'.format(self.source, e.__str__()))

    def spider(self):
        pass

    def main(self):
        pass


if __name__ == '__main__':
    pass
