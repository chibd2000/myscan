# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Certspotter(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.source = 'certspotter'
        self.addr = "https://api.certspotter.com/v1/issuances?domain={}&include_subdomains=true&expand=dns_names"

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), headers=self.headers)
                if 'not_allowed_by_plan' not in text:
                    for _ in eval(text):
                        for subdomain in _['dns_names']:
                            if '*.' in subdomain:
                                subdomain = subdomain.replace('*.', '')
                            self.res_list.append(subdomain)
                else:
                    gLogger.myscan_warn('certspotter api no subdomains.')
        except Exception as e:
            gLogger.myscan_error('curl certspotter api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    cer = Certspotter(domain)
    result = await cer.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('ncist.edu.cn'))
