# coding=utf-8
from spider.thirdLib.third import *



class Fht(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://url.fht.im/domain_search?domain={}"
        self.source = "fht"

    async def spider(self):
        print('Load url.fht.im api ...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr.format(self.domain), headers=self.headers, verify_ssl=False,
                                       timeout=self.reqTimeout) as response:
                    text = await response.text(encoding='utf-8')
                    if 'No Captures found ' not in text:
                        for _ in text.split('\n'):
                            self.resList.append(_)
                    else:
                        print('[-] fht API No Subdomains.')
        except Exception as e:
            print('[-] curl url.fht.im api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    fht = Fht(domain)
    res = await fht.spider()
    return res


if __name__ == '__main__':
    res = do('zjhzu.edu.cn') # not ok
    print(res)