# coding=utf-8

from spider.BaiduSpider import *
from spider.BingSpider import *
from spider.CtfrSpider import *
from spider.NetSpaceSpider import *
from spider.DnsBruteSpider import *
from spider.DnsDataSpider import *
from spider.PortSpider import *
from spider.GithubSpider import *
from spider.JavaScriptSpider import *
from spider.WebParamLinkSpider import *
from spider.StructSpider import *

from common import resolve

from exploit.AliveScan import *
from exploit.IpUnauthExploit import *
from exploit.HttpUnauthExploit import *
from exploit.CmsExploit import *
from exploit.SQLInjectExploit import *
from threading import Thread

import os
import argparse
import time
import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

abs_path = os.getcwd() + os.path.sep  # 路径
thirdLib = abs_path + 'spider/thirdLib/'

gWebParamsList = []  # 存储可注入探测参数列表 ["http://www.baidu.com/?id=1111*"]
gJavaScriptParamList = []  # 存储js文件中的js敏感接口

gIpSegmentDict = {}  # 存储资产IP区段分布以及资产IP在指定的区段出现的次数  {"111.111.111.0/24":1,"111.111.222.0/24":1}
gAsnList = []  # ASN记录
gIpList = []
gTopDomainList = []  # top域名记录
gIpPortList = []


# Spider
class Spider(object):
    def __init__(self, domain):
        self.domain = domain  # 要爬取的域名
        self.threadList = list()  # 线程启动列表
        self.domainList = list()  # 用来存储所有匹配到的域名
        self.clearTaskList = list()  # 存储整理过后的域名 [{"subdomain": "www.ncist.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        self.lock = threading.Lock()

    # github spider
    def ksubdomainSpider(self):
        ksubdomainList = []
        ksubdomain_folder = './ksubdomain'
        ksubdomain_file = '{}/{}.txt'.format(ksubdomain_folder, self.domain)

        os.system(r'./ksubdomain/ksubdomain -d {} -o {}'.format(self.domain, ksubdomain_file))
        try:
            with open(ksubdomain_file, 'rt') as f:
                for each_line in f.readlines():
                    each_line_split = each_line.split('=>')
                    subdomain = each_line_split[0].strip()  # 子域名
                    ksubdomainList.append(subdomain)
            os.remove(ksubdomain_file)  # 删除临时文件
            print('[+] [{}] [{}] {}'.format('ksubdomain', len(ksubdomainList), ksubdomainList))
            self.domainList.extend(ksubdomainList)
        except Exception as e:
            ksubdomains = []

    # baidu Spider
    def baiduSpider(self):
        baidu = BaiduSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(baidu.main())
        resList = loop.run_until_complete(t)
        self.lock.acquire()
        self.domainList.extend(resList)
        self.lock.release()

    # bing Spider
    def bingSpider(self):
        bing = BingSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(bing.main())
        resList = loop.run_until_complete(t)
        self.lock.acquire()
        self.domainList.extend(resList)
        self.lock.release()

    def thirdSpider(self):
        sys.path.append(thirdLib)
        thirdList = filter(lambda x: (True, False)[x[-3:] == 'pyc' or x[-5:] == '__.py' or x[:2] == '__'],
                           os.listdir(thirdLib))

        async def do(future, domain):
            loop = asyncio.get_running_loop()
            res = await loop.create_task(future)
            return res

        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        taskList = []
        for _ in thirdList:
            module = __import__(_[:-3])
            if hasattr(module, 'do'):
                doMethod = getattr(module, 'do')
                # do(doMethod, self.domain)
                taskList.append(loop.create_task(doMethod(self.domain)))
        resList = loop.run_until_complete(asyncio.gather(*taskList))
        for _ in resList:
            self.domainList.extend(_)
        self.domainList = list(set(self.domainList))

    # ssl Spider
    def ctfrSpider(self):
        cftr = CtfrSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(cftr.main())
        ctfrList = loop.run_until_complete(t)
        self.lock.acquire()
        self.domainList.extend(ctfrList)
        self.lock.release()

    # FOFA/Shodan/Quake360
    def netSpider(self):
        global gAsnList, gIpList, gIpPortList
        net = NetSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(net.main())
        netList, gAsnList, gIpList, gIpPortList = loop.run_until_complete(t)
        self.lock.acquire()
        self.domainList.extend(netList)
        self.lock.release()

    # asyncio domain2ip
    def domain2ip(self):
        # logging.info("DomainReserve Start")
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        task = resolve.bulk_query_a(self.clearTaskList)  # 解析域名地址A记录
        self.clearTaskList = loop.run_until_complete(task)

        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[2]
        index = 0
        while index < len(self.clearTaskList):
            # if self.clear_task_list[index]['subdomain'] != '':
            # 只写入子域名解析出来的ip
            if self.domain in self.clearTaskList[index]['subdomain']:
                web = list()
                web.append(self.clearTaskList[index]['subdomain'])
                web.append(self.clearTaskList[index]['ips'])
                worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(self.domain) + ".xlsx")
        workbook.close()

    # resolve ip2domain
    def ip2domain(self):
        logging.info("ip2domainSpider Start")
        global gIpList
        ip2domain_dict = {}
        for ip in gIpList:
            try:
                res = requests.get(url='http://api.webscan.cc/?action=query&ip={}'.format(ip), timeout=10, verify=False)
                text = res.text
                if text != 'null':
                    results = eval(text)
                    domains = []
                    for aDomain in results:
                        domains.append(aDomain['domain'])
                    # domains = cmp.findall(text)
                    if domains:
                        ip2domain_dict[ip] = domains
                        print('[{}] {}'.format(ip, domains))
                        if self.domain:
                            for each in domains:
                                if _domain in each and domain not in each:
                                    newDomains.append(each)
            except Exception as e:
                print('[error] ip2domain: {}'.format(e.args))

        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[4]
        index = 0
        while index < len(ip2domain_dict):
            web = list()
            web.append(ip2domain_dict[index]['spider'])
            web.append(ip2domain_dict[index]['keyword'])
            web.append(ip2domain_dict[index]['link'])
            web.append(ip2domain_dict[index]['title'])
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(self.domain) + ".xlsx")
        workbook.close()

    # github spider
    def githubSpider(self):
        # logging.info("GithubSpider Start")
        # gitLeakList = GithubSpider(self.domain).main()
        # self.lock.acquire()
        # self.domainList.extend(gitLeakList)
        # self.lock.release()
        pass

    # port spider
    def ipPortSpider(self):
        # logging.info("PortScan Start")
        multiprocessing.freeze_support()
        temp_ips = []  # 用来记录扫描过的ip 防止多次扫描 节省时间
        pool = multiprocessing.Pool(5)
        for aaa in self.clearTaskList:
            flag = 0
            if aaa['target'] == 'subdomain':
                if aaa['ips'] != '':
                    # 先进行遍历 验证是否重复扫描
                    for i in temp_ips:
                        if aaa['ips'] == i:
                            flag += 1
                    if flag == 0:
                        temp_ips.append(aaa['ips'])
                        # print("已经扫描过的ip有如下：", temp_ips)
                        bbb = PortScan(self.domain, aaa['ips'])
                        pool.apply_async(func=bbb.main)  # 异步阻塞运行
        pool.close()
        pool.join()

    def flushResult(self):
        # 第一次 清理 去域名协议
        for i in self.task_list:
            if 'http' in i:
                self.task_list[self.task_list.index(i)] = i.split('//')[1]

        # 第二次 清理去重 去重复值
        self.task_list = list(set(self.task_list))

        # 第三次 可视化格式数据拼接
        # 拼接的格式如：[{"subdomain": "www.zjhu.edu.cn","ips": "1.1.1.1","port":[7777,8888],"target","yes"}]
        ip_port = {}
        for aa in self.task_list:
            i = aa.split(':')
            if ':' in aa:
                if str(i[0]) in ip_port.keys():
                    ip_port[str(i[0])].append(str(i[1]))
                else:
                    ip_port[str(i[0])] = [str(i[1])]

        for aa in self.task_list:
            info = dict()
            # 第一种情况：子域名 非正常ip 非正常域名
            if self.domain in aa:
                info['subdomain'] = aa
                info['ip'] = ''
                info['port'] = None
                info['target'] = 'subdomain'  # 作为子域名的一个标识符
                self.clearTaskList.append(info)

            # 第二种情况：非正常子域名 非正常ip 正常域名
            elif self.domain not in aa and not re.match(r'\d+.\d+.\d+:?\d?', aa):
                info['subdomain'] = aa
                info['ip'] = ''
                info['port'] = None
                info['target'] = 'webdomain'
                self.clearTaskList.append(info)

            # 第三种情况：非正常子域名 非正常域名 正常ip
            else:
                i = aa.split(':')
                if ':' in aa:
                    ip = i[0]
                    info['subdomain'] = ''
                    info['ip'] = ip
                    info['port'] = ip_port[ip]
                    info['target'] = 'ip'
                    self.clearTaskList.append(info)
                else:
                    ip = i[0]
                    info['subdomain'] = ''
                    info['ip'] = ip
                    info['port'] = list()
                    info['target'] = 'ip'
                    self.clearTaskList.append(info)

    # 存活探测，限制并发数
    def aliveSpider(self):
        limit_resolve_conn = 500
        semaphore = asyncio.Semaphore(limit_resolve_conn)
        async with semaphore:
            pass

    # main start
    def run(self):
        def checkCdn(domain):
            randomStr = "abcdefghijklmn"

        def getLinks(domain):
            pass
            # 1、https://www.yamibuy.com/cn/brand.php?id=566
            # 2、http://www.labothery-tea.cn/chanpin/2018-07-12/4.html
            # if 'gov.cn' in self.url:
            #     return 0
            #     pass

            # http://www.baidu.com/ -> www.baidu.com/ -> www.baidu.com -> baidu.com

            # domain = domain.split('//')[1].strip('/').replace('www.', '')
            # result = []
            # id_links = []
            # html_links = []
            # result_links = {}
            # html_links_s = []
            # result_links['title'] = '网址标题获取失败'
            # idid = []
            # htht = []
            # try:
            #     headers = {
            #         'Accept': 'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            #         'Cache-Control': 'max-age=0',
            #         'Accept-Charset': 'GBK,utf-8;q=0.7,*;q=0.3',
            #     }
            #     rxww = requests.get(domain, headers=headers, verify=False, timeout=10)
            #     soup = BeautifulSoup(rxww.content, 'html.parser', from_encoding='iso-8859-1')
            #
            #     try:
            #         encoding = requests.utils.get_encodings_from_content(rxww.text)[0]
            #         res = rxww.content.decode(encoding, 'replace')
            #         title_pattern = '<title>(.*?)</title>'
            #         title = re.search(title_pattern, res, re.S | re.I)
            #         result_links['title'] = str(title.group(1))
            #     except:
            #         pass
            #
            #     if result_links['title'] == '' or result_links['title'] == None:
            #         result_links['title'] = '网址标题获取失败'
            #
            #     links = soup.findAll('a')
            #     for link in links:  # 判断是不是一个新的网站
            #         _url = link.get('href')
            #         res = re.search('(javascript|:;|#|%)', str(_url))
            #         res1 = re.search(
            #             '.(jpg|png|bmp|mp3|wma|wmv|gz|zip|rar|iso|pdf|txt)', str(_url))
            #         if res == None and res1 == None:
            #             result.append(str(_url))  # 是的话 那么添加到result列表中
            #         else:
            #             pass
            #     # print(result)
            #     # time.sleep(50)
            #     if result != []:
            #         rst = list(set(result))
            #         for rurl in rst:  # 再进行二次判断是不是子域名 这次的判断有三种情况
            #             if '//' in rurl and 'http' in rurl and domain in rurl:
            #                 # http // domain 都在
            #                 # https://www.yamibuy.com/cn/search.php?tags=163
            #                 # http://news.hnu.edu.cn/zhyw/2017-11-11/19605.html
            #                 if '?' in rurl and '=' in rurl:
            #                     # result_links.append(rurl)
            #                     id_links.append(rurl.strip())
            #                 if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
            #                     if '?' not in rurl:
            #                         # result_links.append(rurl)
            #                         html_links.append(rurl.strip())
            #             # //wmw.dbw.cn/system/2018/09/25/001298805.shtml
            #             if 'http' not in rurl and domain in rurl:
            #                 # http 不在    domain 在
            #                 if '?' in rurl and '=' in rurl:
            #                     id_links.append('http://' + rurl.lstrip('/').strip())
            #                 if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
            #                     if '?' not in rurl:
            #                         html_links.append(
            #                             'http://' + rurl.lstrip('/').strip())
            #
            #             # /chanpin/2018-07-12/3.html"
            #             if 'http' not in rurl and domain not in rurl:
            #                 # http 不在  domain 不在
            #                 if '?' in rurl and '=' in rurl:
            #                     id_links.append(
            #                         'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
            #                 if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
            #                     if '?' not in rurl:
            #                         html_links.append(
            #                             'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
            #
            #         # print(html_links)
            #         # print(id_links)
            #         # time.sleep(50)
            #
            #         for x1 in html_links:  # 对于爬取到的后缀是html等等参数链接进行二次处理 是否能够访问
            #             try:
            #                 rx1 = requests.get(url=x1, headers=headers, timeout=15)
            #                 if rx1.status_code == 200:
            #                     htht.append(x1)
            #             except Exception as e:
            #                 print(e.args)
            #                 pass
            #         for x2 in id_links:  # 平常的id?=1 这种参数进行二次处理 是否能够访问
            #             try:
            #                 rx2 = requests.get(url=x2, headers=headers, timeout=15)
            #                 if rx2.status_code == 200:
            #                     if rx2.url.find('=') > 0:
            #                         idid.append(rx2.url)
            #
            #             except Exception as e:
            #                 print(e.args)
            #                 pass
            #
            #         hthtx = []
            #         ididx = []
            #         dic_1 = []
            #         dic_2 = []
            #         dic_3 = []
            #         dic_4 = []
            #         for i in htht:
            #             path = urlparse(i).path
            #             if path.count('/') == 1:
            #                 dic_1.append(i)
            #             if path.count('/') == 2:
            #                 dic_2.append(i)
            #             if path.count('/') == 3:
            #                 dic_3.append(i)
            #             if path.count('/') > 3:
            #                 dic_4.append(i)
            #         if dic_1:
            #             hthtx.append(random.choice(dic_1))
            #         if dic_2:
            #             hthtx.append(random.choice(dic_2))
            #         if dic_3:
            #             hthtx.append(random.choice(dic_3))
            #         if dic_4:
            #             hthtx.append(random.choice(dic_4))
            #         dic_11 = []
            #         dic_21 = []
            #         dic_31 = []
            #         dic_41 = []
            #         for i in idid:
            #             path = urlparse(i).path
            #             if path.count('/') == 1:
            #                 dic_11.append(i)
            #             if path.count('/') == 2:
            #                 dic_21.append(i)
            #             if path.count('/') == 3:
            #                 dic_31.append(i)
            #             if path.count('/') > 3:
            #                 dic_41.append(i)
            #         if dic_11:
            #             ididx.append(random.choice(dic_11))
            #         if dic_21:
            #             ididx.append(random.choice(dic_21))
            #         if dic_31:
            #             ididx.append(random.choice(dic_31))
            #         if dic_41:
            #             ididx.append(random.choice(dic_41))
            #
            #         if hthtx == []:
            #             pass
            #         else:
            #             result_links['html_links'] = hthtx
            #
            #         if ididx == []:
            #             pass
            #         else:
            #             result_links['id_links'] = ididx
            #
            #     with open('InjEction_links.txt', 'a+', encoding='utf-8')as a:
            #         if ididx:
            #             for i in ididx:
            #                 a.write(i + '\n')
            #         if hthtx:
            #             for u in hthtx:
            #                 a.write(u.replace('.htm', '*.htm').replace('.shtm', '*.shtm') + '\n')
            #
            #     if result_links == {}:
            #         return None
            #     else:
            #         return result_links
            #
            # except Exception as e:
            #     print(e.args)
            # return None

        # 1、checkCdn
        print("======checkCdn======")
        checkCdn(self.domain)

        # 2、大师兄ske用的ksubdomain 自己后面跟着一起
        # 这里进行单一的查询，要不然直接导致带宽不够直接造成其他模块的无法使用
        # dnsbrute_list = subDomaindBrute(self.domain).main()
        # self.lock.acquire()
        # self.task_list.extend(dnsbrute_list)
        # self.lock.release()
        print("======KSubdomain======")
        self.ksubdomainSpider()

        # 3、第三方接口查询
        print("======thirdLibSpider======")
        self.thirdSpider()

        # 4、SSL/engine/netSpace/github查询
        print("======EngineSpider======")
        # self.threadList.append(Thread(target=self.baiduSpider, ))
        # self.threadList.append(Thread(target=self.bingSpider,))
        self.threadList.append(Thread(target=self.ctfrSpider, ))
        self.threadList.append(Thread(target=self.netSpider, ))
        # self.threadList.append(Thread(target=self.githubSpider,))
        # self.threadList.append(Thread(target=self.structSpider,))

        for _ in self.threadList:
            _.start()

        for _ in self.threadList:
            _.join()

        # 5、清洗整理数据
        # self.flushResult()

        # 6、domain2ip
        # self.domain2ip()


        print("=============")
        print('[{}] {}'.format(len(gIpPortList), gIpPortList))
        print("=============")
        print('[{}] {}'.format(len(gAsnList), gAsnList))
        print("=============")
        print('[{}] {}'.format(len(gIpList), gIpList))
        print("=============")
        print('[{}] {}'.format(len(self.domainList), self.domainList))

        # 7、ip2domain
        # self.ip2domain()
        # print(self.clear_task_list)

        # 8、端口扫描，这里的端口扫描自己写的只扫子域名下的ip 可以自行更改target的字段（当走到这里的时候 真正的数据以及格式都是完整的一段数据之后就开始漏洞利用了）
        # self.ipPortSpider()

        # print(self.clearTaskList)

        # 最后返回处理好的数据 交给Exploit类
        return self.clearTaskList


# Exploit
class Exploit(object):
    def __init__(self, domain, clearTaskList):
        self.thread_list = list()
        self.domain = domain
        self.clearTaskList = clearTaskList

    def AliveScan(self):
        AliveScan(self.domain, self.clearTaskList).main()

    def UnauthPortScan(self):
        # [{"subdomain": "www.zjhu.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        queue = asyncio.Queue(-1)
        for aTask in self.clearTaskList:
            aIp = aTask.get('ip')
            aPortList = aTask.get('port')
            for port in aPortList:
                queue.put("{}:{}".format(aIp, port))  # IP+端口, 接下里就是异步socket探测banner来进行相关利用即可.
        IpUnauth(self.domain, queue).main()

    def unauthLeakHttpScan(self):
        HttpUnauth(self.domain, self.clearTaskList).main()

    def cmsLeakScan(self):
        CmsScan(self.domain, self.clearTaskList).main()

    def sqlLeakScan(self):
        # SqlScan(gSubDomainParams).main()
        pass

    def portLeakScan(self):
        # asyncio.open_connection()
        pass

    def jsLeakScan(self):
        # SqlScan(self.domain, self.clear_task_list).main()
        pass

    def run(self):
        def init():
            pass

        self.thread_list.append(Thread(target=self.AliveScan))
        # self.thread_list.append(Thread(target=self.CmsScan))  # cms/框架扫描
        # self.thread_list.append(Thread(target=self.IpUnauthScan))  # 未授权扫描ip
        # self.thread_list.append(Thread(target=self.HttpUnauthScan))  # 未授权扫描http域名
        # self.thread_list.append(Thread(target=self.SqlScan)) # SQL注入扫描

        for i in self.thread_list:
            i.start()

        for i in self.thread_list:
            i.join()


def parse_args():
    parser = argparse.ArgumentParser(prog='MyScan', )
    parser.add_argument('-d', '--domain', type=str, required=True, help="Target domain.")
    parser.add_argument('-f', '--fofa', type=str, help='fofa scan title. for example title=""')
    parser.add_argument('-p', '--scanPort', type=str, help='will all port scan in subdomain.')
    parser.add_argument('-c', '--csegment', type=str, help='csegment. for example 192.168.1.0/24')
    parser.add_argument('-v', '--version', type=str, help='%(prog)s v2')
    return parser.parse_args()


if __name__ == '__main__':
    print('''
        Come From HengGe's Team ^.^
    ''')
    starttime = time.time()
    args = parse_args()
    if args.domain:
        if not os.path.exists(abs_path + args.domain + ".xlsx"):
            createXlsx(args.domain)
        spider = Spider(args.domain)
        clear_task_list = spider.run()
        # exploit = Exploit(args.domain, clear_task_list)
        # exploit.run()
    print("总共耗时时间为：" + str(time.time() - starttime))
