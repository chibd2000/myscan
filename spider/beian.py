# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 13:46

from core.data import gLogger
from spider import BaseSpider
import aiohttp
import re


class BeianSpider(BaseSpider):
    def __init__(self, domain, name):
        super().__init__()
        self.domain = domain
        self.name = name
        self.source = 'Chinaz Beian'
        self.addr1 = 'https://micp.chinaz.com/?query={}'
        self.addr2 = 'https://micp.chinaz.com/Handle/AjaxHandler.ashx?action=GetBeiansl&query={}&type=host'

    async def spider(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr1.format(self.domain), headers=self.headers, timeout=self.reqTimeout, verify_ssl=False, allow_redirects=False) as response:
                    if response is not None:
                        text = await response.text()
                        company_name = re.search('<tr><td class="ww-3 c-39 bg-3fa">主办单位：</td><td class="z-tl">(.*)</td></tr>', text)
                        if company_name:
                            try:
                                async with session.get(url=self.addr2.format(self.domain), headers=self.headers, timeout=self.reqTimeout, verify_ssl=False, allow_redirects=False) as response2:
                                    text = await response2.text()
                                    beian_result = re.findall('SiteLicense:"([^"]*)",SiteName:"([^"]*)",MainPage:"([^"]*)",VerifyTime:"([^"]*)"',text)
                                    if beian_result:
                                        for _ in beian_result:
                                            beian_id, site_name, new_domain, time = _
                                            if new_domain.startswith('www.'):
                                                new_domain = new_domain.replace("www.", '')
                                            self.res_list.append({'SiteLicense': beian_id, 'SiteName': site_name, 'MainPage': new_domain, 'VerifyTime': time})
                            except Exception as e:
                                gLogger.myscan_error('curl {} error, {}'.format(self.addr2, e.args))
                        else:
                            gLogger.myscan_error('没有匹配到公司名')
        except Exception as e:
            gLogger.myscan_error('curl BeianSpider error, {}'.format(self.addr1.format(self.domain), e.args))
        self._is_continue = False
        self.write_file(self.get_unique_list(self.res_list), 0)
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))

    async def main(self):
        await self.spider()


if __name__ == '__main__':
    import asyncio
    beian = asyncio.get_event_loop().run_until_complete(BeianSpider('zjhu.edu.cn', '').main())
