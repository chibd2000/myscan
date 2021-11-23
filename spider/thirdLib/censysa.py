# coding=utf-8
from aiohttp import BasicAuth

from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Censys(BaseThird):
    """
    censys third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.source = 'censys'
        self.addr = 'https://search.censys.io/api/v1/search/certificates'
        self.id = config.censysId
        self.secret = config.censysSecret

    async def spider(self):
        print('[+] Load censys api ...')
        auth = BasicAuth(login=self.id, password=self.secret)
        try:
            async with aiohttp.ClientSession() as session:
                data = {'query': f'parsed.names: {self.domain}', 'page': 1,
                        'fields': ['parsed.subject_dn', 'parsed.names'], 'flatten': True}
                async with session.post(url=self.addr, data=json.dumps(data), verify_ssl=False, auth=auth,
                                        timeout=self.reqTimeout) as response:
                    retJson = await response.json()
                    try:
                        pages = retJson['metadata']['pages']
                    except ValueError:
                        print('[-] censys No data query.')
                        return []
                page = 0
                while page <= pages:
                    data = {'query': f'parsed.names: {self.domain}', 'page': page,
                            'fields': ['parsed.subject_dn', 'parsed.names'], 'flatten': True}
                    async with session.post(url=self.addr, data=json.dumps(data), verify_ssl=False, auth=auth,
                                            timeout=self.reqTimeout) as response:
                        text = await response.text()
                        subdomainList = self.matchSubdomain(self.domain, text)
                        self.resList.extend(subdomainList)
                    page += 1
        except Exception as e:
            print('[-] curl search.censys.io error, the error is {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    censysa = Censys(domain)
    res = await censysa.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do('huolala.cn'))
