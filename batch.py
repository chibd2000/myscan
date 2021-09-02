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
from spider.ip2domainSpider import *
from spider.ParamLinkSpider import *
from spider.FriendChainsSpider import *
from spider.StructSpider import *
from spider.AliveSpider import *

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
from IPy import IP

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

abs_path = os.getcwd() + os.path.sep  # 路径
thirdLib = abs_path + 'spider/thirdLib/'

gParamsList = []  # 存储可注入探测参数列表 ["http://www.baidu.com/?id=1111*"]
gJavaScriptParamList = []  # 存储js文件中的js敏感接口

gIpSegmentList = []  # 存储资产IP区段分布以及资产IP在指定的区段出现的次数  [{"111.111.111.0/24":1},{"111.111.222.0/24":1}]
gAsnList = []  # ASN记录
gIpList = []  # 用来统计gIpSegmentDict
gTopDomainList = []  # top域名记录


# Spider
class Spider(object):
    def __init__(self, domain):
        self.domain = domain  # 要爬取的域名
        self.threadList = []  # 线程启动列表
        self.domainList = []  # 用来存储所有匹配到的子域名和一些隐形资产
        self.ipPortList = []
        self.clearTaskList = []  # 存储整理过后的域名 [{"subdomain": "www.ncist.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        self.lock = threading.Lock()

    # github spider
    def ksubdomainSpider(self):
        logging.info("ksubdomainSpider Start")
        ksubdomainList = []
        ksubdomain_folder = './ksubdomain'
        ksubdomain_file = '{}/{}.txt'.format(ksubdomain_folder, self.domain)
        os.system('./ksubdomain/ksubdomain -d {} -o {}'.format(self.domain, ksubdomain_file))
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
        logging.info("baiduSpider Start")
        baidu = BaiduSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resList = loop.run_until_complete(baidu.main())
        self.lock.acquire()
        self.domainList.extend(resList)
        self.lock.release()

    # bing Spider
    def bingSpider(self):
        logging.info("bingSpider Start")
        bing = BingSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resList = loop.run_until_complete(bing.main())
        self.lock.acquire()
        self.domainList.extend(resList)
        self.lock.release()

    # third Spider
    def thirdSpider(self):
        logging.info("thirdSpider Start")
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

    # ssl Spider
    def ctfrSpider(self):
        logging.info("CtfrSpider Start")
        cftr = CtfrSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(cftr.main())
        resList = loop.run_until_complete(t)
        self.lock.acquire()
        self.domainList.extend(resList)
        self.lock.release()

    # github spider
    def githubSpider(self):
        logging.info("githubSpider Start")
        cftr = GithubSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(cftr.main())
        resList = loop.run_until_complete(t)
        self.lock.acquire()
        self.domainList.extend(resList)
        self.lock.release()

    # FOFA/Shodan/Quake360
    def netSpider(self):
        logging.info("netSpider Start")
        global gAsnList, gIpList
        net = NetSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(net.main())
        resList, gAsnList, gIpList, self.ipPortList = loop.run_until_complete(t)
        self.lock.acquire()
        self.domainList.extend(resList)
        self.lock.release()

    # 友链爬取
    def friendChainsSpider(self):
        logging.info("friendChainsSpider Start")
        # queue = asyncio.Queue(-1)
        # for domain in self.domainList:
        #     queue.put(domain)
        friend = FriendChainsSpider(self.domain, self.domainList)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(friend.main())
        resList = loop.run_until_complete(t)
        self.lock.acquire()
        self.domainList.extend(resList)
        self.domainList = list(set(self.domainList))
        self.lock.release()

    # asyncio domain2ip
    def domain2ip(self):
        logging.info("domain2ipSpider Start")
        ip2domainList = []
        for subdomain in self.domainList:
            ip2domainList.append({'subdomain': subdomain, 'ip': ''})
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        task = resolve.bulk_query_a(ip2domainList)  # 解析域名地址A记录
        resolvedomain2IpList = loop.run_until_complete(task)
        global gIpList
        for _ in resolvedomain2IpList:
            gIpList.append(_['ip'])
        gIpList = list(set(gIpList))
        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[3]
        index = 0
        while index < len(resolvedomain2IpList):
            # if self.clear_task_list[index]['subdomain'] != '':
            # 只写入子域名解析出来的ip
            if self.domain in resolvedomain2IpList[index]['subdomain']:
                web = list()
                web.append(resolvedomain2IpList[index]['subdomain'])
                web.append(resolvedomain2IpList[index]['ip'])
                worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(self.domain) + ".xlsx")
        workbook.close()

    # resolve ip2domain
    def ip2domain(self):
        logging.info("ip2domainSpider Start")
        global gIpList
        gIpList = [i for i in gIpList if i != '']  # 清洗一遍，这里面可能存在一个''，空字符串
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        ip2domainSpider = Ip2domainSpider(self.domain, gIpList)
        resList = loop.run_until_complete(ip2domainSpider.main())
        self.lock.acquire()
        self.domainList.extend(resList)
        self.domainList = list(set(self.domainList))
        self.lock.release()

    # port spider
    # def ipPortSpider(self):
    #     logging.info("PortSpider Start")
    #     multiprocessing.freeze_support()
    #     temp_ips = []  # 用来记录扫描过的ip 防止多次扫描 节省时间
    #     pool = multiprocessing.Pool(5)
    #     for aaa in self.clearTaskList:
    #         flag = 0
    #         if aaa['target'] == 'subdomain':
    #             if aaa['ips'] != '':
    #                 # 先进行遍历 验证是否重复扫描
    #                 for i in temp_ips:
    #                     if aaa['ips'] == i:
    #                         flag += 1
    #                 if flag == 0:
    #                     temp_ips.append(aaa['ips'])
    #                     # print("已经扫描过的ip有如下：", temp_ips)
    #                     bbb = PortScan(self.domain, aaa['ips'])
    #                     pool.apply_async(func=bbb.main)  # 异步阻塞运行
    #     pool.close()
    #     pool.join()

    def ipPortSpider(self):
        logging.info("portSpider Start")
        pass

    # 存活探测，限制并发数
    def aliveSpider(self):
        global gParamsList
        logging.info("aliveSpider Start")
        aliveSpider = AliveSpider(self.domain, self.domainList)
        loop = asyncio.get_event_loop()
        resList = loop.run_until_complete(aliveSpider.main())
        gParamsList.extend(resList)

    # main start
    def run(self):
        # 检查cdn @author ske大师兄
        def checkCdn(domain):
            logging.info("checkCdn start")

            randomStr = "abcdefghijklmn"

        # 整理数据，相关格式之类的整理
        def flushResult(domain):
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
                if domain in aa:
                    info['subdomain'] = aa
                    info['ip'] = ''
                    info['port'] = None
                    info['target'] = 'subdomain'  # 作为子域名的一个标识符
                    self.clearTaskList.append(info)

                # 第二种情况：非正常子域名 非正常ip 正常域名
                elif domain not in aa and not re.match(r'\d+.\d+.\d+:?\d?', aa):
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

        # 整理数据，去除cdn段的asn 去除cdn段的节点段 @ske大师兄
        def flushIpSegment(domain):
            global gIpList, gIpSegmentList
            tempIpSegmentList = getIpSegment(gIpList)
            for ipSegment in tempIpSegmentList:
                gIpSegmentList.append({'ipSegment': ipSegment, 'ip': [], 'num': 0})
            for ip in gIpList:
                for ipSegment in tempIpSegmentList:
                    ipList = IP(ipSegment)
                    for i in ipList:
                        if str(ip) == str(i):
                            for j in gIpSegmentList:
                                if j.get('ipSegment') == ipSegment:
                                    j['num'] += 1
                                    j['ip'].append(ip)
            workbook = openpyxl.load_workbook(abs_path + str(domain) + ".xlsx")
            worksheet = workbook.worksheets[4]
            index = 0
            while index < len(gIpSegmentList):
                web = list()
                web.append(gIpSegmentList[index]['ipSegment'])
                web.append(str(gIpSegmentList[index]['ip']))
                web.append(gIpSegmentList[index]['num'])
                worksheet.append(web)
                index += 1
            workbook.save(abs_path + str(domain) + ".xlsx")
            workbook.close()

        def flushAsn(domain):
            global gAsnList
            workbook = openpyxl.load_workbook(abs_path + str(domain) + ".xlsx")
            worksheet = workbook.worksheets[5]
            index = 0
            while index < len(gAsnList):
                web = list()
                web.append(gAsnList[index])
                worksheet.append(web)
                index += 1
            workbook.save(abs_path + str(domain) + ".xlsx")
            workbook.close()

        global gAsnList, gIpList, gIpSegmentList

        # 1、checkCdn
        checkCdn(self.domain)

        # 2、大师兄ske用的ksubdomain 自己后面跟着一起
        # 这里进行单一的查询，要不然直接导致带宽不够直接造成其他模块的无法使用
        # dnsbrute_list = subDomaindBrute(self.domain).main()
        # self.lock.acquire()
        # self.task_list.extend(dnsbrute_list)
        # self.lock.release()
        # self.ksubdomainSpider()

        # 3、第三方接口查询
        self.thirdSpider()

        # 4、SSL/engine/netSpace/github查询
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

        # 6、友链爬取
        self.friendChainsSpider()

        # 7、domain2ip
        self.domain2ip()

        # 8、ip2domain
        self.ip2domain()

        # 9、alive
        self.aliveSpider()

        # 10、port scan in self.ipPortList
        # self.ipPortSpider()

        # 11、asn和ip段整理
        flushIpSegment(self.domain)
        flushAsn(self.domain)

        # 去重子域名
        self.domainList = list(set(self.domainList))
        print("=============")
        print('[+] [gAsnList] [{}] {}'.format(len(gAsnList), gAsnList))
        print("=============")
        print('[+] [gIpList] [{}] {}'.format(len(gIpList), gIpList))
        print("=============")
        print('[+] [gIpSegmentList] [{}] {}'.format(len(gIpSegmentList), gIpSegmentList))
        print("=============")
        print('[+] [gParamsList] [{}] {}'.format(len(gParamsList), gParamsList))
        print("=============")
        print('[+] [ipPortList] [{}] {}'.format(len(self.ipPortList), self.ipPortList))
        print("=============")
        print('[+] [domainList] [{}] {}'.format(len(self.domainList), self.domainList))

        # 最后返回处理好的数据 交给Exploit类
        return self.domainList, self.ipPortList


# Exploit
class Exploit(object):
    def __init__(self, domain, domainList, IpPortList):
        self.thread_list = list()
        self.domain = domain
        self.domainList = domainList
        self.IpPortList = IpPortList

    def AliveScan(self):
        pass
        # AliveScan(self.domain, self.domainList).main()

    def UnauthPortScan(self):
        pass
        # [{"subdomain": "www.zjhu.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        queue = asyncio.Queue(-1)
        for aTask in self.domainList:
            aIp = aTask.get('ip')
            aPortList = aTask.get('port')
            for port in aPortList:
                queue.put("{}:{}".format(aIp, port))  # IP+端口, 接下里就是异步socket探测banner来进行相关利用即可.
        IpUnauth(self.domain, queue).main()

    def unauthLeakHttpScan(self):
        HttpUnauth(self.domain, self.domainList).main()

    def jsExploit(self):
        # SqlScan(self.domain, self.clear_task_list).main()
        pass

    # 基于网站参数的漏扫
    def sqlExploit(self):
        # [{"subdomain": "www.zjhu.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        global gParamsList
        queue = asyncio.Queue(-1)
        for aTask in gParamsList:
            pass
        #     queue.put("{}:{}".format(aIp, port))  # IP+端口, 接下里就是异步socket探测banner来进行相关利用即可.
        # IpUnauth(self.domain, queue).main()

    # 基于网站框架的漏扫
    def webExploit(self):
        # [{"subdomain": "www.zjhu.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        queue = asyncio.Queue(-1)
        for aTask in self.domainList:
            aIp = aTask.get('ip')
            aPortList = aTask.get('port')
            for port in aPortList:
                queue.put("{}:{}".format(aIp, port))  # IP+端口, 接下里就是异步socket探测banner来进行相关利用即可.
        IpUnauth(self.domain, queue).main()

    # 基于端口服务的漏扫
    def serviceExploit(self):
        # [{"subdomain": "www.zjhu.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        queue = asyncio.Queue(-1)
        for aTask in self.IpPortList:
            aIp = aTask.get('ip')
            aPortList = aTask.get('port')
            for port in aPortList:
                queue.put("{}:{}".format(aIp, port))  # IP+端口, 接下里就是异步socket探测banner来进行相关利用即可.
        IpUnauth(self.domain, queue).main()

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
    parser.add_argument('-p', '--scanport', type=str, help='will all port scan in subdomain.')
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
            domainList, ipPortList = spider.run()
            # exploit = Exploit(args.domain, domainList, ipPortList)
            # exploit.run()

        else:
            print('文件{}.xlsx已存在，如果要运行的话需要将该文件{}.xlsx改名或者删除.'.format(args.domain, args.domain))
    print("总共耗时时间为：" + str(time.time() - starttime))
