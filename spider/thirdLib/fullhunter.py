# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class FullHunter(BaseSpider):
    """
    FullHunter third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.source = 'fullhunter'
        self.addr = 'https://fullhunt.io/api/v1/domain/{}/subdomains'
        self.domain = domain
        self.api = '2ab13b3a-8867-4734-9d97-303100eb1204'

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        if not self.api:
            gLogger.myscan_warn('{} no api.'.format(self.source))
            return []
        headers = self.headers.copy()
        headers.update({'X-API-KEY': self.api})
        try:
            async with aiohttp.ClientSession() as session:
                ret_json = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), headers=headers, timeout=self.reqTimeout, json=True)
                if 'hosts' in ret_json.keys():
                    self.res_list = ret_json['hosts']
                elif 'domain_not_found' in str(ret_json):
                    gLogger.myscan_warn('{} - your domain is not found.'.format(self.source))
                else:
                    gLogger.myscan_warn('{} - api no subdomains.'.format(self.source))
        except Exception as e:
            gLogger.myscan_error('curl fullhunter.io api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    full_hunter = FullHunter(domain)
    result = await full_hunter.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
