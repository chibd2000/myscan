# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class Fht(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://url.fht.im/domain_search?domain={}'
        self.source = 'fht'

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        try:
            async with aiohttp.ClientSession() as session:
                text = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), headers=self.headers, timeout=self.reqTimeout)
                if 'No Captures found ' not in text:
                    for _ in text.split('\n'):
                        if _:
                            self.res_list.append(_)
                else:
                    gLogger.myscan_warn('fht api no subdomains.')
        except Exception as e:
            print('[-] curl url.fht.im api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    fht = Fht(domain)
    result = await fht.spider()
    return result


if __name__ == '__main__':
    res = do('zjhzu.edu.cn')  # not ok
    print(res)
