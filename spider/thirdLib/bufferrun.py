# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 21:25
from core.data import gLogger, config_dict
from spider import BaseSpider
from core.request.asynchttp import AsyncFetcher
import aiohttp
import asyncio


class Bufferover(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = "http://dns.bufferover.run/dns?q=.{}"
        self.source = 'bufferover'

    async def get_subdomain(self, proxy):
        try:
            async with aiohttp.ClientSession() as session:
                result_list = []
                ret_json = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), proxy=proxy, timeout=self.reqTimeout, json=True)
                dns_a_value = ret_json['FDNS_A']
                if dns_a_value:
                    for _ in dns_a_value:
                        subdomain = _.split(',')[-1]
                        result_list.append(subdomain)
                    return result_list
                else:
                    gLogger.myscan_warn('{} no subdomains.'.format(self.source))
        except TimeoutError:
            gLogger.myscan_error('curl dns.bufferover.run error, the error is Timeout.')
        except ConnectionRefusedError:
            gLogger.myscan_error('curl dns.bufferover.run error, the error is ConnectionRefused.')
        except Exception as e:
            gLogger.myscan_error('curl dns.bufferover.run error, the error is {}'.format(e.args))

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))

        async def getProxy():
            url = 'https://api.proxyscrape.com/?request=displayproxies&proxytype=http&country=all&anonymity=all&ssl=yes'
            try:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    proxy = config_dict['proxy']
                    text = await AsyncFetcher.fetch(session=session, url=url, proxy=proxy, timeout=self.reqTimeout)
                    if text:
                        proxy_list = [x for x in text.split('\r\n') if x != '']
                        gLogger.myscan_info('curl api.proxyscrape.com grabbed proxy success.')
                        return proxy_list
                    else:
                        gLogger.myscan_warn('curl api.proxyscrape.com grabbed proxy fail.')
            except aiohttp.ClientHttpProxyError:
                gLogger.myscan_error('curl api.proxyscrape.com need outer proxy.')
                return []
            except asyncio.TimeoutError:
                gLogger.myscan_error('curl api.proxyscrape.com timeout, check your proxy.')
                return []
            except Exception as e:
                gLogger.myscan_warn('curl api.proxyscrape.com error, thr error is {}'.format(e.args))
                return []
        proxy_list = await asyncio.create_task(getProxy())
        if proxy_list:
            task_list = []
            for _ in proxy_list:
                task_list.append(asyncio.create_task(self.get_subdomain(_)))
            result_list = await asyncio.gather(*task_list)
            for _ in result_list:
                if _ is None:
                    continue
                self.res_list.extend(_)
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    bufferover = Bufferover(domain)
    result = await bufferover.spider()
    return result


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(do('nbcc.cn'))
