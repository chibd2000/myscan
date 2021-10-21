# coding=utf-8
from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Hacketarget(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://api.hackertarget.com/hostsearch/?q={}"
        self.source = "hacktarget"

    async def spider(self):
        print('Load hackertarget api ...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr.format(self.domain), headers=self.headers, verify_ssl=False, timeout=self.reqTimeout, proxy='http://192.168.0.108:7890') as response:
                    text = await response.text()
                    if text != 'error check your search parameter':
                        for _ in text.split('\n'):
                            subdomain = _.split(',')[0]
                            self.resList.append(subdomain)
                    else:
                        print('[-] hackertarget API No Subdomains.')
        except Exception as e:
            print('[-] curl api.hackertarget.com api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    hackTarget = Hacketarget(domain)
    res = await hackTarget.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
