# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 23:53

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Securitytrails(BaseSpider):
    """
    securitytrails third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://api.securitytrails.com/v1/domain/{}/subdomains?children_only=false&include_inactive=true'
        self.source = 'securitytrails'
        self.api = config_dict['securitytrails']

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        if not self.api:
            gLogger.myscan_warn('{} no api.'.format(self.source))
            return []
        headers = self.headers.copy()
        headers.update({'APIKEY': self.api, 'Accept': 'application/json'})
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), json=True)
                results = text.get('subdomains', '')
                if results:
                    for _ in results:
                        self.res_list.append('{}.{}'.format(_, self.domain))
                else:
                    gLogger.myscan_warn('securitytrails api no subdomains.')
        except Exception as e:
            gLogger.myscan_error('curl api.securitytrails.com error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    s = Securitytrails(domain)
    result = await s.spider()
    return result

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('huolala.cn'))
