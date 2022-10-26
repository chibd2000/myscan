# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-31 23:04

from core.data import gLogger
from core.request import asynchttp
from spider import BaseSpider

import asyncio


class FriendChainsSpider(BaseSpider):
    def __init__(self, domain, domainList):
        super().__init__()
        self.source = 'FriendChainsSpider'
        self.domain = domain
        self.res_list = domainList

    async def get_friend_domain(self, temp_domain_list):
        new_domain_list = []
        if temp_domain_list:
            try:
                result = await asynchttp.AsyncFetcher.fetch_all(urls=temp_domain_list, headers=self.headers, takeover=True, timeout=10)
                for _ in result:
                    new_domain_list.extend(self.match_subdomain(self.domain, _[1]))
                new_domain_list.extend(temp_domain_list)
                new_domain_list = list(set(new_domain_list))
                cha_domain_list = list(set(new_domain_list) - set(self.res_list))
                # gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))
                self.res_list.extend(cha_domain_list)
                self.res_list = list(set(self.res_list))
                await self.get_friend_domain(cha_domain_list)
            except asyncio.CancelledError as e:
                gLogger.myscan_error('friendChainSpider Task was cancelled, error is {}'.format(e.args))
            except Exception as e:
                gLogger.myscan_error('[-] curl is error, error is {}'.format(e.args))

    async def spider(self):
        await self.get_friend_domain(self.res_list)
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))

    async def main(self):
        await self.spider()
        return self.res_list


if '__main__' == __name__:
    # queue = asyncio.Queue(-1)
    # FriendChainsSpider('nbcc.cn', queue).main()
    baidu = FriendChainsSpider('zjhu.edu.cn', ['qzxylib.zjhu.edu.cn', '61.153.52.74', 'wgyxy.zjhu.edu.cn', 'ic.zjhu.edu.cn', 'rwxy.qzxy.zjhu.edu.cn',
         'tzb.zjhu.edu.cn', 'dag.zjhu.edu.cn', 'yjsy.zjhu.edu.cn'])
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(baidu.main())
