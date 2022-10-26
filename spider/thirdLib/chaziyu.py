# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger
from spider import BaseSpider
import aiohttp
import re


class Chaziyu(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://chaziyu.com/{}"
        self.source = "chaziyu"

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), headers=self.headers, timeout=self.reqTimeout)
                results = re.findall(r'target="_blank">(.*\.{})</a></td>'.format(self.domain), text)
                for _ in results:
                    self.res_list.append(_)
        except Exception as e:
            gLogger.myscan_error('curl chaziyu.com api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    chaziyu = Chaziyu(domain)
    result = await chaziyu.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
