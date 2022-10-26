# coding=utf-8
from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Virustotal(BaseSpider):
    """
    virustotal third spider
    """
    def __init__(self, domain):
        super().__init__()
        self.addr = 'https://www.virustotal.com/vtapi/v2/domain/report?apikey={}&domain={}'
        self.domain = domain
        self.api = config_dict['virustotal']
        self.source = 'virustotal'

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            if not self.api:
                gLogger.myscan_warn('{} no api.'.format(self.source))
                return []
            async with aiohttp.ClientSession() as session:
                ret_json = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.api, self.domain), headers=self.headers, json=True)
                if 'Domain not found' in str(ret_json):
                    gLogger.myscan_warn('{} - error invalid host.'.format(self.source))
                    return []
                if 'subdomains' in ret_json.keys():
                    self.res_list = ret_json['subdomains']
        except Exception as e:
            print('[-] curl virustotal.com api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    virustotal = Virustotal(domain)
    res = await virustotal.spider()
    return res


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
