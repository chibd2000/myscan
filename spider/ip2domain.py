# coding=utf-8
from core.data import gLogger
from core.request.asynchttp import AsyncFetcher
from spider import BaseSpider
import aiohttp
import asyncio


class Ip2domainSpider(BaseSpider):
    def __init__(self, domain, name, ip_list):
        super().__init__()
        self.name = name
        self.source = 'Ip2domainSpider'
        self.domain = domain
        self.ip_list = ip_list
        self.addr = 'http://api.webscan.cc/?action=query&ip={}'

    async def get_subdomain(self, semaphore, ip, ip2domainList):
        try:
            async with semaphore:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    text = await AsyncFetcher.fetch(session=session, url=self.addr.format(ip))
                    if text != 'null':
                        results = eval(text)
                        domains = []
                        for each in results:
                            domains.append(each['domain'])
                        if domains:
                            ip2domainList.append({'ip': ip, 'domain': str(domains)})
                            # gLogger.myscan_info('[{}] {}'.format(ip, domains))
                            for _ in domains:
                                if self.domain in _:
                                    self.res_list.append(_)
        except Exception as e:
            gLogger.myscan_error('[-] curl api.webscan.cc error, the error is {}'.format(e.args))

    async def spider(self):
        concurrency = 50  # 这里的话稍微控制下并发量
        semaphore = asyncio.Semaphore(concurrency)
        ip2_domain_list = []
        task_list = [asyncio.create_task(self.get_subdomain(semaphore, ip, ip2_domain_list)) for ip in self.ip_list]
        await asyncio.gather(*task_list)
        self._is_continue = False
        self.write_file(self.get_unique_list(ip2_domain_list), 7)
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))

    async def main(self):
        await self.spider()
        return self.res_list


if __name__ == '__main__':
    testList = ['61.153.52.11', '61.153.52.74', '61.153.52.57', '61.153.52.20', '211.80.146.74', '61.153.52.23',
                '211.80.146.57', '61.153.52.103', '61.153.52.24', '61.153.52.21', '61.153.52.68', '61.153.52.52']
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    w = Ip2domainSpider('zjhu.edu.cn', testList)
    t = loop.run_until_complete(w.main())
    print(t)
