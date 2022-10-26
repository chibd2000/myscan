# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-29 3:05


from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Entrust(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://ctsearch.entrust.com/api/v1/certificates'
        self.source = 'entrust'

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                params = {'fields': 'subjectDN', 'domain': self.domain, 'includeExpired': 'true'}
                ret_json = await AsyncFetcher.fetch(session=session, url=self.addr, params=params, json=True, headers=self.headers)
                for _ in ret_json:
                    self.res_list.append(_['subjectDN'].split(',')[0].replace('cn=', '').replace('*.', ''))
        except Exception as e:
            gLogger.myscan_error('curl ctsearch.entrus.com error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    entrus = Entrust(domain)
    result = await entrus.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
