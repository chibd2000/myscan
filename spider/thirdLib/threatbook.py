# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:10

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Threatbook(BaseSpider):
    """
    threatbook third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.source = 'threatbook'
        self.domain = domain
        self.addr = 'https://api.threatbook.cn/v3/domain/sub_domains?apikey={API_KEY}&resource={DOMAIN}'
        self.api = config_dict['threatbook']

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            if not self.api:
                gLogger.myscan_warn('{} no api.'.format(self.source))
                return []
            async with aiohttp.ClientSession(headers=self.headers) as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(API_KEY=self.api, DOMAIN=self.domain))
                if 'No Access to API Method' in text:
                    gLogger.myscan_warn('{} - api key is not access.'.format(self.source))
                    return []
                self.res_list.extend(self.match_subdomain(self.domain, text))
        except Exception as e:
            gLogger.myscan_error('curl threatbook.cn api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    threatbook = Threatbook(domain)
    result = await threatbook.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
