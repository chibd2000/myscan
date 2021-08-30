# coding=utf-8
from spider.thirdLib.third import *


class Rapiddns(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://rapiddns.io/subdomain/{}#result"

    async def spider(self):
        print('Load rapiddns api ...')
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain))
                results = re.findall(r'<th scope="row ">\d+</th>\n<td>(.*?)</td>', text, re.S | re.I)
                if results:
                    for _ in results:
                        self.resList.append(_)
                else:
                    print('rapiddns API No Subdomains.')
        except Exception as e:
            print('[-] curl rapiddns api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[{}] {}'.format(len(self.resList), self.resList))
        return self.resList


async def do(domain):
    rapiddns = Rapiddns(domain)
    res = await rapiddns.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))