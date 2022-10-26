# coding=utf-8

from core.request.asynchttp import AsyncFetcher
from core.data import gLogger, config_dict
from spider import BaseSpider
import aiohttp
import json


class Censys(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.source = 'censys'
        self.addr = 'https://search.censys.io/api/v1/search/certificates'
        self.id = config_dict['censys']['censys_id']
        self.secret = config_dict['censys']['censys_secret']

    async def spider(self):
        gLogger.myscan_debug('Load {} api ...'.format(self.source))
        if not self.id or not self.secret:
            gLogger.myscan_warn('{} no api.'.format(self.source))
            return []
        try:
            auth = aiohttp.BasicAuth(login=self.id, password=self.secret)
            async with aiohttp.ClientSession() as session:
                data = {'query': f'parsed.names: {self.domain}', 'page': 1, 'fields': ['parsed.subject_dn', 'parsed.names'], 'flatten': True}
                ret_json = await AsyncFetcher.post_fetch(session=session, url=self.addr, auth=auth, data=json.dumps(data), timeout=self.reqTimeout, json=True)
                try:
                    pages = ret_json['metadata']['pages']
                except ValueError:
                    gLogger.myscan_error('censys api no subdomains')
                    return []
                page = 0
                while page <= pages:
                    data = {'query': f'parsed.names: {self.domain}', 'page': page, 'fields': ['parsed.subject_dn', 'parsed.names'], 'flatten': True}
                    ret_text = await AsyncFetcher.post_fetch(session=session, url=self.addr, auth=auth, data=json.dumps(data), timeout=self.reqTimeout)
                    subdomain_list = self.match_subdomain(self.domain, ret_text)
                    self.res_list.extend(subdomain_list)
                    page += 1
        except Exception as e:
            gLogger.myscan_error('search.censys.io error, the error is {}'.format(e.args))
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
        return self.res_list


async def do(domain):
    censys = Censys(domain)
    result = await censys.spider()
    return result


if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(do('huolala.cn'))
