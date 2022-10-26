# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger
from spider import BaseSpider
import aiohttp


class Ximcx(BaseSpider):
    """
     ximcx third spider
     """
    def __init__(self, domain):
        super().__init__()
        self.addr = 'http://sbd.ximcx.cn/DomainServlet'
        self.source = 'ximcx'
        self.domain = domain

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                results = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), json=True)
                code = results['code']
                if code == 0:
                    for _ in results['data']:
                        subdomain = _['domain']
                        self.res_list.append(subdomain)
                else:
                    gLogger.myscan_warn('{} api no subdomains.'.format(self.source))
                    return []
        except Exception as e:
            gLogger.myscan_error('curl ximcx api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    ximcx = Ximcx(domain)
    res = await ximcx.spider()
    return res


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
