# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:01

from spider.thirdLib.third import *


class Jldc(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://jldc.me/anubis/subdomains/{}"
        self.source = 'jidc'

    async def spider(self):
        print('Load Jidc api ...')
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain))
                result = eval(text)
                if result:
                    for _ in result:
                        self.resList.append(_)
                else:
                    print('Jldc API No Subdomains.')
        except Exception as e:
            print('[-] curl jldc.me api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    alien = Jldc(domain)
    res = await alien.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('nbcc.cn'))
