# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:13

from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Alien(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://otx.alienvault.com/api/v1/indicators/domain/{}/passive_dns"
        self.source = "alienvault"

    async def spider(self):
        print('[+] Load alienvault api ...')
        try:
            # async with aiohttp.ClientSession() as session:
            #     async with session.get(url=self.addr.format(self.domain), headers=self.headers, verify_ssl=False,
            #                            timeout=self.reqTimeout) as response:
            #         text = await response.json(encoding='utf-8')
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), json=True)
                res = text['passive_dns']
                if res:
                    for _ in res:
                        self.resList.append(_.get('hostname'))
                else:
                    print('[-] alienvault API No Subdomains.')
        except Exception as e:
            print('[-] curl otx.alienvault.com api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    alien = Alien(domain)
    domainList = await alien.spider()
    return domainList


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))

