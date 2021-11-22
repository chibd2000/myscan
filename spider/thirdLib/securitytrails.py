# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 23:53

from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Securitytrails(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://api.securitytrails.com/v1/domain/{}/subdomains?children_only=false&include_inactive=true'
        self.source = 'securitytrails'
        self.api = config.securitytrailsApi

    async def spider(self):
        print('[+] Load securitytrails api ...')
        headers = self.headers.copy()
        headers.update({'APIKEY': self.api, 'Accept': 'application/json'})
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), json=True)
                results = text.get('subdomains', '')
                if results:
                    for _ in results:
                        self.resList.append('{}.{}'.format(_, self.domain))
                else:
                    print('securitytrails API No Subdomains.')
        except Exception as e:
            print('[-] curl securitytrails api error, the error is {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [securitytrails] [{}] {}'.format(len(self.resList), self.resList))
        return self.resList


async def do(domain):
    s = Securitytrails(domain)
    res = await s.spider()
    return res

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('huolala.cn'))
