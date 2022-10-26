# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp
import re


class Rapiddns(BaseSpider):
    """
    rapiddns third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://rapiddns.io/subdomain/{}#result'
        self.source = 'rapiddns'

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain))
                results = re.findall(r'<th scope="row ">\d+</th>\n<td>(.*?)</td>', text, re.S | re.I)
                if results:
                    for _ in results:
                        self.res_list.append(_)
                else:
                    gLogger.myscan_warn('rapiddns api no subdomains.')
        except Exception as e:
            gLogger.myscan_error('curl rapiddns.io error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    rapiddns = Rapiddns(domain)
    result = await rapiddns.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
