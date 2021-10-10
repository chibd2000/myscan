# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 23:46

from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Chinaz(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://api.sublist3r.com/search.php?domain={}"
        self.source = 'chinaz'
        self.api = config.chinazApi

    async def spider(self):
        print('Load chinaz api ...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr.format(self.api, self.domain), headers=self.headers,
                                       verify_ssl=False,
                                       timeout=self.reqTimeout) as response:
                    if response is not None:
                        text = await response.text()
                        if text != 'null':
                            for subdomain in eval(text):
                                self.resList.append(subdomain)
                        else:
                            print('chinaz API No Subdomains.')
        except Exception as e:
            print('[-] curl chinaz.com api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


# async def do(domain):
#     chinaz = Chinaz(domain)
#     res = await chinaz.spider()
#     return res


if __name__ == '__main__':
    pass
    # loop = asyncio.get_event_loop()
    # res = loop.run_until_complete(do('zjhu.edu.cn'))
