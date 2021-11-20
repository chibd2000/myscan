# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 21:25
from spider.thirdLib.public import *
from spider.thirdLib import BaseThird


class Bufferover(BaseThird):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "http://dns.bufferover.run/dns?q=.{}"
        self.source = 'bufferover'

    async def getSubdomain(self, proxy):
        try:
            # proxies = {'http': f'http:{proxy}', 'https': f'https:{proxy}'}
            # resList = []
            # scraper = cfscrape.create_scraper()  # 绕Cloudflare验证码
            # resp = scraper.get(url=self.addr.format(self.domain), headers=self.headers, verify=False,
            #                    timeout=self.reqTimeout, proxies=proxies)
            # text = resp.text
            # FDNS_A_value = json.loads(text)['FDNS_A']
            # if FDNS_A_value:
            #     for _ in FDNS_A_value:
            #         subdomain = _.split(',')[-1]
            #         resList.append(subdomain)
            #     return resList
            # else:
            #     print('bufferover API No Subdomains.')
            async with aiohttp.ClientSession(headers=self.headers) as session:
                proxies = 'http://{}'.format(proxy)
                resList = []
                async with session.get(url=self.addr.format(self.domain), verify_ssl=False, timeout=10, proxy=proxies) as response:
                    text = await response.text(encoding='utf-8')
                    FDNS_A_value = json.loads(text)['FDNS_A']
                    if FDNS_A_value:
                        for _ in FDNS_A_value:
                            subdomain = _.split(',')[-1]
                            resList.append(subdomain)
                        return resList
                    else:
                        print('[-] bufferover API No Subdomains.')
        except Exception as e:
            print('[-] curl dns.bufferover.run api error. {}'.format(e.__str__()))

    async def spider(self):
        async def getProxy():
            url = 'https://api.proxyscrape.com/?request=displayproxies&proxytype=http&country=all&anonymity=all&ssl=yes&timeout=2000'
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(url=url, verify_ssl=False, timeout=self.reqTimeout, proxy='http://127.0.0.1:7890') as response:
                        if response is not None:
                            text = await response.text()
                            if text:
                                proxyList = [x for x in text.split('\r\n') if x != '']
                                print('[+] curl api.proxyscrape.com grabbed proxy success.')
                                return proxyList
                            else:
                                print('[-] curl api.proxyscrape.com grabbed proxy fail.')
            except aiohttp.ClientHttpProxyError:
                print('[-] curl api.proxyscrape.com need outer proxy.')
            except asyncio.TimeoutError:
                print("[-] curl api.proxyscrape.com timeout, check your proxy.")
                return []

        print('[+] Load bufferover api ...')
        t = asyncio.create_task(getProxy())
        proxyList = await t
        taskList = []
        for _ in proxyList:
            taskList.append(asyncio.create_task(self.getSubdomain(_)))
        res = await asyncio.gather(*taskList)
        for aList in res:
            if aList is None:
                continue
            self.resList.extend(aList)
        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList


async def do(domain):
    bufferover = Bufferover(domain)
    res = await bufferover.spider()
    return res


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('nbcc.cn'))
