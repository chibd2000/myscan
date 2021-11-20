# coding=utf-8

from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Certspotter(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://api.certspotter.com/v1/issuances?domain={}&include_subdomains=true&expand=dns_names"
        self.source = 'certspotter'

    async def spider(self):
        print('[+] Load certspotter api ...')
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain))
                if 'not_allowed_by_plan' not in text:
                    for _ in eval(text):
                        for subdomain in _['dns_names']:
                            if '*.' in subdomain:
                                subdomain = subdomain.replace('*.', '')
                            self.resList.append(subdomain)
                else:
                    print('certspotter API No Subdomains.')
        except Exception as e:
            print('[-] curl certspotter api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    cer = Certspotter(domain)
    res = await cer.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('ncist.edu.cn'))
