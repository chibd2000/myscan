# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger
from spider import BaseSpider
import aiohttp
import time
import re


class Qianxun(BaseSpider):
    """
    qianxun third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'http://www.dnsscan.cn/dns.html'
        self.source = 'qianxun'

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        headers = self.headers.copy()
        headers.update({'Upgrade': 'http/1.1'})
        try:
            async with aiohttp.ClientSession() as session:
                page = 1
                while True:
                    time.sleep(0.25)
                    params = {'ecmsfrom': '8.8.8.8', 'show': 'none', 'keywords': self.domain, 'page': page}
                    text = await AsyncFetcher.post_fetch(session=session, url=self.addr, data=params, headers=headers, timeout=self.reqTimeout)
                    re_data = re.findall(r'<a href="http[s]?://(.*?)"\srel', text, flags=re.S)[1:]
                    if re_data:
                        self.res_list.extend(re_data)
                    else:
                        break
                    page += 1
        except Exception as e:
            gLogger.myscan_error('curl dnsscan.cn error, the error is {}'.format(e.args))
        for value in enumerate(self.res_list.copy()):
            if '*' in value:
                self.res_list.remove(value)
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    qianxun = Qianxun(domain)
    result = await qianxun.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
