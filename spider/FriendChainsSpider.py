# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-31 23:04

from core.public import *
from spider import BaseSpider


class FriendChainsSpider(BaseSpider):
    def __init__(self, domain, domainList: list):
        super().__init__()
        self.domain = domain
        self.resList = domainList
        self.source = 'FriendChainsSpider'

    def writeFile(self, web_lists, page):
        pass

    async def spider(self):
        # sslInfo = []
        # try:
        # async with aiohttp.ClientSession(headers=self.headers) as session:
        #     result = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), json=True)
        #     for (key, value) in enumerate(result):
        #         subdomainSSL = value['name_value'].split('\n')
        #         if len(subdomainSSL) == 2:
        #             domainInfo = {'ssl': subdomainSSL[0], 'subdomain': subdomainSSL[1]}
        #             self.resList.append(subdomainSSL[1])
        #         else:
        #             domainInfo = {'ssl': 'None', 'subdomain': subdomainSSL[0]}
        #             self.resList.append(subdomainSSL[0])
        #
        #         # 一起放到列表中进行存储
        #         sslInfo.append(domainInfo)
        # except Exception as e:
        #     print('[-] curl crt.sh error. {}'.format(e.args))
        try:
            tempDomainList = []
            # limit_resolve_conn = 100
            # semaphore = asyncio.Semaphore(limit_resolve_conn)
            # async with semaphore:
            result = await AsyncFetcher.fetchAll(urls=self.resList, takeover=True)
            for _ in result:
                matchdomainList = self.matchSubdomain(self.domain, _[1])
                _matchdomainList = list(set(matchdomainList))
                for domain in _matchdomainList:
                    flag = True
                    for _domain in self.resList:
                        if str(domain) == str(_domain):
                            flag = False
                            break
                    if flag:
                        tempDomainList.append(domain)  # 存放新的子域名的列表
            print('[+] [new friendChains] [{}] {}'.format(len(tempDomainList), tempDomainList))
            self.resList.extend(tempDomainList)
            self.resList = list(set(self.resList))

            while tempDomainList:
                result = await AsyncFetcher.fetchAll(urls=tempDomainList, takeover=True)
                tempDomainList = []
                for _ in result:
                    matchdomainList = self.matchSubdomain(self.domain, _[1])
                    _matchdomainList = list(set(matchdomainList))
                    for domain in _matchdomainList:
                        flag = True
                        for _domain in self.resList:
                            if str(domain) == str(_domain):
                                flag = False
                                break
                        if flag:
                            tempDomainList.append(domain)  # 存放新的子域名的列表
                tempDomainList = list(set(tempDomainList))
                print('[+] [new friendChains] [{}] {}'.format(len(tempDomainList), tempDomainList))
                self.resList.extend(tempDomainList)
        except asyncio.CancelledError as e:
            print('[-] friendChainSpider Task was cancelled, error is {}'.format(e.args))
        except Exception as e:
            print('[-] curl is error, error is {}'.format(e.args))

        # 返回结果
        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))

    async def main(self):
        await self.spider()
        return self.resList


if '__main__' == __name__:
    # queue = asyncio.Queue(-1)
    # FriendChainsSpider('nbcc.cn', queue).main()
    baidu = FriendChainsSpider('zjhu.edu.cn',
        ['qzxylib.zjhu.edu.cn', '61.153.52.74', 'wgyxy.zjhu.edu.cn', 'ic.zjhu.edu.cn', 'rwxy.qzxy.zjhu.edu.cn',
         'tzb.zjhu.edu.cn', 'dag.zjhu.edu.cn', 'yjsy.zjhu.edu.cn'])
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(baidu.main())
