# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-29 3:05


from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Entrus(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://ctsearch.entrust.com/api/v1/certificates"
        self.source = 'entrus'

    # async def spider(self):
    #     print('Load rapiddns api ...')
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain))
    #             results = re.findall(r'<th scope="row ">\d+</th>\n<td>(.*?)</td>', text, re.S | re.I)
    #             if results:
    #                 for _ in results:
    #                     self.resList.append(_)
    #             else:
    #                 print('rapiddns API No Subdomains.')
    #     except Exception as e:
    #         print('[-] curl rapiddns api error. {}'.format(e.args))
    #
    #     self.resList = list(set(self.resList))
    #     print('[{}] {}'.format(len(self.resList), self.resList))
    #     return self.resList

    async def spider(self):
        print('Load entrus api ...')
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                params = {'fields': 'subjectDN', 'domain': self.domain, 'includeExpired': 'true'}
                result = await AsyncFetcher.fetch(session=session, url=self.addr, params=params, json=True)
                print(result)
                for _ in result:
                    self.resList.append(_['subjectDN'].split(',')[0].replace('cn=', '').replace('*.', ''))
        except Exception as e:
            print('[-] curl entrus.com api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    entrus = Entrus(domain)
    res = await entrus.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
