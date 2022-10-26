# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 23:46

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Chinaz(BaseSpider):
    """
    chinaz third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://apidata.chinaz.com/CallAPI/Alexa'
        self.source = 'chinaz'
        self.api = config_dict['chinaz']

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            if not self.api:
                gLogger.myscan_warn('{} no api.'.format(self.source))
                return []
            async with aiohttp.ClientSession() as session:
                params = {'key': self.api, 'domainName': self.domain}
                text = await AsyncFetcher.fetch(session=session, url=self.addr, params=params, headers=self.headers, timeout=self.reqTimeout)
                if '"StateCode":10001' in text:
                    gLogger.myscan_warn('{} - api key is not correct'.format(self.source))
                    return []
                elif '"StateCode":0' in text:
                    gLogger.myscan_warn('{} - api no subdomains.'.format(self.source))
                    return []
                elif '"StateCode":1' in text:
                    self.res_list.extend(self.match_subdomain(self.domain, text))
        except Exception as e:
            gLogger.myscan_error('curl chinaz.com api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    chinaz = Chinaz(domain)
    result = await chinaz.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('zjhu.edu.cn'))
