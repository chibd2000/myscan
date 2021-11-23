# coding=utf-8
from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Sublist3r(BaseThird):
    """
    sublist3r third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://api.sublist3r.com/search.php?domain={}'
        self.source = 'sublist3r'

    async def spider(self):
        print('[+] Load sublist3r api ...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr.format(self.domain), headers=self.headers, verify_ssl=False,
                                       timeout=self.reqTimeout) as response:
                    text = await response.text(encoding='utf-8')
                    if text != 'null':
                        for _ in eval(text):
                            self.resList.append(_)
                    else:
                        print('[-] Sublist3r API No Subdomains.')
        except Exception as e:
            print('[-] curl api.sublist3r.com api error, the error is {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    sublist3r = Sublist3r(domain)
    res = await sublist3r.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('huolala.cn'))
