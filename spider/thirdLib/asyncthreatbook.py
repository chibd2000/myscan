# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:10

from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Threatbook(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://api.threatbook.cn/v3/domain/sub_domains?apikey={API_KEY}&resource={DOMAIN}"
        self.api = config.threatbookApi
        self.source = 'threatbook'

    async def spider(self):
        print('Load threatbook api ...')
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                text = await AsyncFetcher.fetch(session=session,
                                                url=self.addr.format(API_KEY=self.api, DOMAIN=self.domain))
        except Exception as e:
            print('[-] curl threatbook.cn api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    threatbook = Threatbook(domain)
    res = await threatbook.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
