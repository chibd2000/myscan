# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp
import re


class Sitedossier(BaseSpider):
    """
    sitedossier third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'http://www.sitedossier.com/parentdomain/{}'
        self.source = 'sitedossier'

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain))
                if 'No data currently available' in text:
                    gLogger.myscan_warn('{} api no subdomains.'.format(self.source))
                results = re.findall(r'<a href="/site/(.*\.{})">'.format(self.domain), text)
                if results:
                    for _ in results:
                        self.res_list.append(_)
                elif 'No data currently available' in text:
                    gLogger.myscan_warn('{} api no subdomains.'.format(self.source))
        except Exception as e:
            gLogger.myscan_error('curl sitedossier api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    site = Sitedossier(domain)
    result = await site.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
