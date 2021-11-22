# coding=utf-8
from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Sitedossier(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'http://www.sitedossier.com/parentdomain/{}'
        self.source = 'sitedossier'

    async def spider(self):
        print('[+] Load sitedossier api ...')
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain))
                results = re.findall(r'<a href="/site/(.*\.{})">'.format(self.domain), text)
                if results:
                    for _ in results:
                        self.resList.append(_)
                else:
                    print('[-] sitedossier API No Subdomains.')
        except Exception as e:
            print('[-] curl sitedossier api error, the error is {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    site = Sitedossier(domain)
    res = await site.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
