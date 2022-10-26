# coding=utf-8
from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Sublist3r(BaseSpider):
    """
    sublist3r third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://api.sublist3r.com/search.php?domain={}'
        self.source = 'sublist3r'

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), timeout=self.reqTimeout)
                if text != 'null':
                    for _ in eval(text):
                        self.res_list.append(_)
                else:
                    gLogger.myscan_warn('sublist3r api no subdomains.')
                    return []
        except Exception as e:
            gLogger.myscan_error('curl api.sublist3r.com api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    sublist3r = Sublist3r(domain)
    result = await sublist3r.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('huolala.cn'))
