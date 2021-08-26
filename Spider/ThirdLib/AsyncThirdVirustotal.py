# coding=utf-8
from Spider.ThirdLib.Third import *


class Virustotal(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.addr = 'https://www.virustotal.com/vtapi/v2/domain/report?apikey={}&domain={}'
        self.domain = domain
        self.api = virustotalApi
        self.source = "virustotal"

    async def spider(self):
        print('Load VirusTotal api ...')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr.format(self.api, self.domain), headers=self.headers, verify_ssl=False,
                                       timeout=self.reqTimeout) as response:
                    text = await response.text(encoding='utf-8')
                    if response.status == 403:
                        print('VirusTotal API Permission error.')
                    elif response.status == 200:
                        ret_json = json.loads(text)
                        if 'subdomains' in ret_json.keys():
                            self.resList = ret_json['subdomains']
                    else:
                        print('VirusTotal API No Subdomains.')
        except Exception as e:
            print('[-] curl virustotal.com api error.')

        self.resList = list(set(self.resList))
        print('[{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    virustotal = Virustotal(domain)
    res = await virustotal.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
