# coding=utf-8

from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Ximcx(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.addr = 'http://sbd.ximcx.cn/DomainServlet'
        self.domain = domain

    async def spider(self):
        print('[+] Load ximcx api ...')
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                results = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), json=True)
                code = results['code']
                if code == 0:
                    for _ in results['data']:
                        subdomain = _['domain']
                        self.resList.append(subdomain)
                else:
                    print('ximcx API No Subdomains.')
        except Exception as e:
            print('[-] curl ximcx api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


async def do(domain):
    ximcx = Ximcx(domain)
    res = await ximcx.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
