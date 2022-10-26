# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 0:00

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp


class BinaryedgeError(Exception):
    def __init__(self, message):
        self.mesage = message


class Binaryedge(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "https://api.binaryedge.io/v2/query/domains/subdomain/{}?page={}"
        self.source = 'binaryedge'
        self.api = config_dict['binaryedge']

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        if not self.api:
            gLogger.myscan_warn('{} no api.'.format(self.source))
            return []
        try:
            page = 1
            async with aiohttp.ClientSession() as session:
                self.headers.update({'X-Key': self.api})
                while 1:
                    try:
                        ret_json = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain, page), headers=self.headers, json=True)
                        if 'Could not validate token' in str(ret_json):
                            raise BinaryedgeError(ret_json['message']) from None
                        if ret_json['events']:
                            for _ in ret_json['events']:
                                self.res_list.append(_)
                        else:
                            break
                    except BinaryedgeError as e:
                        gLogger.myscan_error('[{}] {}'.format(self.source, e.mesage))
                        break
                    except Exception:
                        gLogger.myscan_error('binaryedge api no subdomains')
                        break
                    page += 1
        except Exception as e:
            gLogger.myscan_error('curl binaryedge.io api error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    binaryedge = Binaryedge(domain)
    result = await binaryedge.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('ncist.edu.cn'))
