# coding=utf-8
from spider.BaseSpider import *

from queue import Queue
from threading import Thread

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
TIMEOUT = 10
cmp = re.compile(r'{"domain":"http:\\/\\/(.*?)","title":".*?"}')  # 正则匹配规则


class Ip2domainSpider(Spider):
    def __init__(self):
        super().__init__()
        self.source = 'ip2domain'
        self.addr = 'http://api.webscan.cc/?action=query&ip={}'

    def writeFile(self, web_lists, page):
        workbook = openpyxl.load_workbook(abs_path + str(random) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(web_lists[index]['spider'])
            web.append(web_lists[index]['keyword'])
            web.append(web_lists[index]['link'])
            web.append(web_lists[index]['title'])
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(random) + ".xlsx")
        workbook.close()

    def ip2domain(self, allTargets_Queue, domain, _domain, ip2domain_dict, newDomains):
        while not allTargets_Queue.empty():
            ip = allTargets_Queue.get()
            try:
                res = requests.get(url=self.addr, headers=headers, timeout=TIMEOUT, verify=False)
                text = res.text
                if text != 'null':
                    results = eval(text)
                    domains = []
                    for each in results:
                        domains.append(each['domain'])
                    # domains = cmp.findall(text)
                    if domains:
                        ip2domain_dict[ip] = domains
                        print('[{}] {}'.format(ip, domains))
                        if domain:
                            for each in domains:
                                if _domain in each and domain not in each:
                                    newDomains.append(each)
            except Exception as e:
                print('[error] ip2domain: {}'.format(e.args))

    def spider(self):
        pass

    def main(self):
        pass


if __name__ == '__main__':
    pass
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
