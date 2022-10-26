# coding=utf-8

from core.data import gLogger
from spider import BaseSpider
from core.request.asynchttp import AsyncFetcher
import aiohttp


class CeBaidu(BaseSpider):
    """
    ceBaidu third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "http://ce.baidu.com/index/getRelatedSites?site_address={}"
        self.source = "cebaidu"

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                ret_json = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), timeout=self.reqTimeout, json=True)
                if isinstance(ret_json, dict) and 'data' in ret_json.keys():
                    for _ in ret_json['data']:
                        self.res_list.append(_['domain'])
                else:
                    gLogger.myscan_warn('cebaidu api no subdomains.')
        except Exception as e:
            gLogger.myscan_error('curl ce.baidu.com api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    baidu = CeBaidu(domain)
    res = await baidu.spider()
    return res


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
