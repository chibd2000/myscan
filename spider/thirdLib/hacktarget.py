# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Hacketarget(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://api.hackertarget.com/hostsearch/?q={}'
        self.source = 'hacktarget'

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                proxy = config_dict['proxy']
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), headers=self.headers, proxy=proxy)
                if text != 'error check your search parameter':
                    for _ in text.split('\n'):
                        subdomain = _.split(',')[0]
                        self.res_list.append(subdomain)
                elif 'error invalid host' in text:
                    gLogger.myscan_warn('{} - error invalid host.'.format(self.source))
                else:
                    gLogger.myscan_warn('{} - api no subdomains.'.format(self.source))
        except aiohttp.ClientHttpProxyError:
            gLogger.myscan_error('curl api.hackertarget.com need outer proxy.')
            return []
        except Exception as e:
            gLogger.myscan_error('curl api.hackertarget.com api error, the error is {}'.format(e.args))
            return []
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    hacktarget = Hacketarget(domain)
    result = await hacktarget.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('baidu.com'))
