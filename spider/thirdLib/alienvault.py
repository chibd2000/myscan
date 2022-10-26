# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:13

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Alien(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://otx.alienvault.com/api/v1/indicators/domain/{}/passive_dns"
        self.source = "alienvault"

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                proxy = config_dict['proxy']
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), proxy=proxy, timeout=self.reqTimeout, json=True)
                result = text['passive_dns']
                if result:
                    for _ in result:
                        self.res_list.append(_.get('hostname'))
                else:
                    gLogger.warn('[{}] alienvault api no subdomains'.format(self.source))
        except Exception as e:
            gLogger.myscan_error('curl otx.alienvault.com api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    alien = Alien(domain)
    result = await alien.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
