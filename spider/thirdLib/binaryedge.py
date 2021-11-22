# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:00

from spider.thirdLib.public import *
from spider.thirdLib import BaseThird

class Binaryedge(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://api.binaryedge.io/v2/query/domains/subdomain/{}?page={}"
        self.source = 'binaryedge'
        self.api = config.binaryedgeApi
        self.headers.update({'X-Key': self.api})

    async def spider(self):
        print('[+] Load binaryedge api ...')
        try:
            # resp = requests.get(url=self.addr.format(self.domain), headers=self.headers, verify=False, timeout=self.reqTimeout)
            # results = re.findall(r'<th scope="row ">\d+</th>\n<td>(.*)</td>'.format(self.domain), text, re.S | re.I)
            # if results:
            #     for _ in results:
            #         self.resList.append(resp)
            # else:
            #     print('Binaryedge API No Subdomains.')
            page = 1
            async with aiohttp.ClientSession(headers=self.headers) as session:
                while 1:
                    result = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain, page), json=True)
                    if result['events']:
                        for _ in result['events']:
                            self.resList.append(_)
                    else:
                        print('[-] binaryedge API No Subdomains.')
                        break
                    page += 1
        except Exception as e:
            print('[-] curl binaryedge.io api error, the error is {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source,len(self.resList), self.resList))
        return self.resList


async def do(domain):
    binaryedge = Binaryedge(domain)
    res = await binaryedge.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('ncist.edu.cn'))
