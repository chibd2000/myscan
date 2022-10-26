# coding=utf-8
from core.data import gLogger
from spider import BaseSpider
import aiohttp
import asyncio


class CrtSpider(BaseSpider):
    def __init__(self, domain, name):
        super().__init__()
        self.name = name
        self.domain = domain
        self.addr = 'https://crt.sh/?q=%.{}&output=json'
        self.source = 'CrtSpider'

    async def spider(self):
        ssl_info = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr.format(self.domain), verify_ssl=False) as response:
                    text = await response.json()
                    for (key, value) in enumerate(text):
                        sub_domain = value['name_value'].split('\n')
                        if len(sub_domain) == 2:
                            domain_info = {'ssl': sub_domain[0], 'subdomain': sub_domain[1]}
                            self.res_list.append(sub_domain[1])
                        else:
                            domain_info = {'ssl': 'None', 'subdomain': sub_domain[0]}
                            self.res_list.append(sub_domain[0])
                        # 一起放到列表中进行存储
                        ssl_info.append(domain_info)
        except aiohttp.ClientHttpProxyError:
            gLogger.myscan_error('curl ctfr.sh need outer proxy.')
            return []
        except Exception as e:
            gLogger.myscan_error('curl crt.sh error, the erorr is {}'.format(e.args))
            return []
        self._is_continue = False
        self.write_file(self.get_unique_list(ssl_info), 3)
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))

    async def main(self):
        await self.spider()
        return self.res_list


if '__main__' == __name__:
    baidu = CrtSpider('huolala.cn')
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(baidu.main())
