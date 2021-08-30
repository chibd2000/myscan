# coding=utf-8
from spider.thirdLib.third import *



class CeBaidu(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "http://ce.baidu.com/index/getRelatedSites?site_address={}"
        self.source = "cebaidu"

    async def spider(self):
        print('Load ceBaidu api ...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr.format(self.domain), headers=self.headers, verify_ssl=False,
                                       timeout=self.reqTimeout) as response:
                    text = await response.text(encoding='utf-8')
                    ret_json = json.loads(text)
                    if 'data' in ret_json.keys():
                        for _ in ret_json['data']:
                            self.resList.append(_['domain'])
                    else:
                        print('[-] CeBaidu API No Subdomains.')
        except Exception as e:
            print('[-] curl ce.baidu.com api error. {}'.format(e.args))

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    baidu = CeBaidu(domain)
    res = await baidu.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
