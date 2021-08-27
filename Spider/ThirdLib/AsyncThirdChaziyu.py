from Spider.ThirdLib.Third import *


class Chaziyu(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://chaziyu.com/{}"
        self.source = "chaziyu"

    async def spider(self):
        print('Load chaziyu api ...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr.format(self.domain), headers=self.headers, verify_ssl=False,
                                       timeout=self.reqTimeout) as response:
                    text = await response.text(encoding='utf-8')
                    status_code = response.status
                    if status_code != 404:
                        results = re.findall(r'target="_blank">(.*\.{})</a></td>'.format(self.domain), text)
                        for _ in results:
                            self.resList.append(_)
                    else:
                        print('[-] chaziyu API No Subdomains.')
        except Exception as e:
            print('[-] curl chaziyu.com api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    chaziyu = Chaziyu(domain)
    res = await chaziyu.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
