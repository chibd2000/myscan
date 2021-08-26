# coding=utf-8
from Spider.ThirdLib.Third import *


class Qianxun(ThirdBase):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://www.dnsscan.cn/dns.html"
        self.source = "qianxun"
        self.headers.update({'Upgrade': 'http/1.1'})

    async def spider(self):
        print('Load qianxun api ...')
        try:
            async with aiohttp.ClientSession() as session:
                page = 1
                while True:
                    time.sleep(0.25)
                    params = {'ecmsfrom': '8.8.8.8', 'show': 'none', 'keywords': self.domain, 'page': page}
                    async with session.post(url=self.addr, data=params, headers=self.headers,
                                            verify_ssl=False, timeout=self.reqTimeout) as response:
                        text = await response.text(encoding='utf-8')
                        re_data = re.findall(r'<a href="(.*?)"\srel', text, flags=re.S)[1:]
                        if re_data:
                            self.resList.extend(re_data)
                        else:
                            break
                    page += 1
        except Exception as e:
            print('[-] curl dnsscan.cn api error. {}'.format(e.args))

        for value in enumerate(self.resList.copy()):
            if '*' in value:
                self.resList.remove(value)
        self.resList = list(set(self.resList))
        print('[{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    qianxun = Qianxun(domain)
    res = await qianxun.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('nbcc.cn'))
