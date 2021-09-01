# coding=utf-8
# @Author   : ske
from spider.BaseSpider import *

def getUniqueList(L):
    (output, temp) = ([], [])
    for l in L:
        for k, v in l.items():
            flag = False
            if (k, v) not in temp:
                flag = True
                break
        if flag:
            output.append(l)
        temp.extend(l.items())
    return output
class Ip2domainSpider(Spider):
    def __init__(self, domain, gIpList):
        super().__init__()
        self.source = 'ip2domain'
        self.domain = domain
        self.ipList = gIpList
        self.addr = 'http://api.webscan.cc/?action=query&ip={}'

    def writeFile(self, web_lists, page):
        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(web_lists[index]['ip'])
            web.append(web_lists[index]['domain'])
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(self.domain) + ".xlsx")
        workbook.close()

    async def getSubdomain(self, semaphore, ip, ip2domainList):
        try:
            async with semaphore:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    text = await AsyncFetcher.fetch(session=session, url=self.addr.format(ip))
                    if text != 'null':
                        results = eval(text)
                        domains = []
                        for each in results:
                            domains.append(each['domain'])
                        if domains:
                            ip2domainList.append({'ip': ip, 'domain': str(domains)})
                            print('[{}] {}'.format(ip, domains))
                            for _ in domains:
                                if self.domain in _:
                                    self.resList.append(_)
                    await asyncio.sleep(1)

        except Exception as e:
            print('[error] ip2domain: {} {}'.format(ip, e.args))

    async def spider(self):
        concurrency = 50  # 这里的话稍微控制下并发量
        semaphore = asyncio.Semaphore(concurrency)
        ip2domainList = []
        taskList = [asyncio.create_task(self.getSubdomain(semaphore, ip, ip2domainList)) for ip in self.ipList]
        await asyncio.gather(*taskList)
        # 写文件
        self.writeFile(getUniqueList(ip2domainList), 7)
        # 返回结果
        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))

    async def main(self):
        await self.spider()
        return self.resList


if __name__ == '__main__':
    testList = ['61.153.52.11', '61.153.52.74', '61.153.52.57', '61.153.52.20', '211.80.146.74', '61.153.52.23',
                '211.80.146.57', '61.153.52.103', '61.153.52.24', '61.153.52.21', '61.153.52.68', '61.153.52.52']
    loop = asyncio.get_event_loop()
    asyncio.set_event_loop(loop)
    w = Ip2domainSpider('zjhu.edu.cn', testList)
    t = loop.run_until_complete(w.main())
    print(t)
    # domain = ''
    # allTargets_Queue = Queue(-1)
    # allTargets_Queue.put('')
    # allTargets_Queue.put('')
    # ip2domain_dict, _newDomains = run_ip2domain(domain, allTargets_Queue)
    # # for ip in ip2domain_dict:
    # #     print('[{}] -> {}'.format(ip, ip2domain_dict[ip]))
    #
    # print(ip2domain_dict)
    # subdomains = []
    # for subdomain in ip2domain_dict.values():
    #     subdomains.extend(subdomain)
    #
    # setSubdomains = list(set(subdomains))
    # print('[{}] {}'.format(len(setSubdomains), setSubdomains))
    # print(_newDomains)

#
