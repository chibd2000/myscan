# coding=utf-8

from core.MyModuleLoader import ModuleLoader
from core.MyConstant import ModulePath
from core.utils.FuzzDifflib import MyDifflib
from core.utils.PortWrapper import PortWrapper
from core.MyLogger import Logger
from core.MyGlobalVariableManager import GlobalVariableManager

from spider.BeianSpider import BeianSpider
from spider.BaiduSpider import BaiduSpider
from spider.BingSpider import BingSpider
from spider.CtfrSpider import CtfrSpider
from spider.NetSpaceSpider import NetSpider
from spider.StructSpider import CompanyStructSpider
# from spider.DnsBruteSpider import *
# from spider.DnsDataSpider import *
from spider.PortSpider import PortScan
from spider.GithubSpider import GithubSpider
from spider.ip2domainSpider import Ip2domainSpider
from spider.FriendChainsSpider import FriendChainsSpider
from spider.AliveSpider import AliveSpider

from common import resolve

# from exploit.AliveScan import *
# from exploit.IpUnauthExploit import *
# from exploit.HttpUnauthExploit import *
from exploit.CmsExploit import *
# from exploit.SQLExploit import *
from exploit.ServiceExploit import *

from threading import Thread, Lock
import os
import argparse
import time
import sys
import asyncio
import importlib
from IPy import IP

version = sys.version.split()[0]
if version < "3":
    exit(
        "[-] Incompatible Python version detected ('%s'). For successfully running program you'll have to use version "
        "3  (visit 'http://www.python.org/download/')" % version)

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# if sys.platform == 'win32':
#     loop = asyncio.ProactorEventLoop()
#     asyncio.set_event_loop(loop)

abs_path = os.getcwd() + os.path.sep  # 路径
# gPortRegister = []  # 存储用于portSpider模块中要扫描的端口
gParserConfig = {}

gDomainList = []  # 用来存储所有匹配到的子域名和一些隐形资产
gDomainAliveList = []
gIpPortServiceList = []
gWebParamsList = []  # 存储可注入探测参数列表 ["http://www.baidu.com/?id=1111*"]
gLogger = Logger('./log/logs.txt')

# Spider
class Spider(object):
    def __init__(self, domain):
        self.threadList = []  # 线程启动列表
        self.ipSegmentList = []  # 存储资产IP区段分布以及资产IP在指定的区段出现的次数  [{"111.111.111.0/24":1},{"111.111.222.0/24":1}]
        self.asnList = []  # ASN记录
        self.ipList = []  # 用来统计gIpSegmentDict
        self.ipPortList = []  # 存储端口+服务
        self.topDomainList = []  # 存储顶级域名记录 @ske
        self.javaScriptParamList = []  # 存储js文件中的js敏感接口 @小洲师傅
        self.domain = domain
        self.clearTaskList = []  # 存储整理过后的域名 [{"subdomain": "www.zjhu.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        self.lock = Lock()
        # self.moduleLoader = ModuleLoader()

    # beian spider
    def beianSpider(self):
        gLogger.info("BeianSpider Start")
        beian = BeianSpider(self.domain)
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(beian.main())

    # github spider
    def ksubdomainSpider(self):
        gLogger.info("KSubdomainSpider Start")
        global gDomainList
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
            gDomainList.extend(ksubdomainList)
        except Exception as e:
            ksubdomains = []

    # baidu Spider
    def baiduSpider(self):
        gLogger.info("BaiduSpider Start")
        global gDomainList
        baidu = BaiduSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resList = loop.run_until_complete(baidu.main())
        self.lock.acquire()
        gDomainList.extend(resList)
        self.lock.release()

    # bing Spider
    def bingSpider(self):
        gLogger.info("BingSpider Start")
        global gDomainList
        bing = BingSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        resList = loop.run_until_complete(bing.main())
        self.lock.acquire()
        gDomainList.extend(resList)
        self.lock.release()

    # third Spider
    def thirdSpider(self):
        gLogger.info("ThirdSpider Start")
        global gDomainList
        sys.path.append(abs_path + ModulePath.THIRDLIB)
        thirdModuleList = filter(lambda x: (True, False)[x[-3:] == 'pyc' or x[-5:] == '__.py' or x[:2] == '__'],
                                 os.listdir(abs_path + ModulePath.THIRDLIB))

        async def do(future, domain):
            loop = asyncio.get_running_loop()
            res = await loop.create_task(future)
            return res

        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        taskList = []
        for _ in thirdModuleList:
            module = importlib.import_module(_[:-3])
            if hasattr(module, 'do'):
                doMethod = getattr(module, 'do')
                # do(doMethod, self.domain)
                taskList.append(loop.create_task(doMethod(self.domain)))
        resList = loop.run_until_complete(asyncio.gather(*taskList))
        for _ in resList:
            self.lock.acquire()
            gDomainList.extend(_)
            self.lock.release()

    # ssl Spider
    def ctfrSpider(self):
        gLogger.info("CtfrSpider Start")
        global gDomainList
        cftr = CtfrSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(cftr.main())
        resList = loop.run_until_complete(t)
        self.lock.acquire()
        gDomainList.extend(resList)
        self.lock.release()

    # github spider
    def githubSpider(self):
        gLogger.info("GithubSpider Start")
        global gDomainList
        github = GithubSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(github.main())
        resList = loop.run_until_complete(t)
        self.lock.acquire()
        gDomainList.extend(resList)
        self.lock.release()

    # FOFA/Shodan/Quake360
    def netSpider(self):
        gLogger.info("NetSpider Start")
        global gDomainList
        net = NetSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(net.main())
        resList, self.asnList, self.ipList, self.ipPortList = loop.run_until_complete(t)
        self.lock.acquire()
        gDomainList.extend(resList)
        self.lock.release()

    # 友链爬取
    def friendChainsSpider(self):
        gLogger.info("FriendChainsSpider Start")
        global gDomainList
        # queue = asyncio.Queue(-1)
        # for domain in self.domainList:
        #     queue.put(domain)
        friend = FriendChainsSpider(self.domain, gDomainList)
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(friend.main())
        resList = loop.run_until_complete(t)
        self.lock.acquire()
        gDomainList.extend(resList)
        gDomainList = list(set(gDomainList))
        self.lock.release()

    # asyncio domain2ip
    def domain2ip(self):
        gLogger.info("Domain2ipSpider Start")
        global gDomainList
        ip2domainList = []
        for subdomain in gDomainList:
            ip2domainList.append({'subdomain': subdomain, 'ip': ''})
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        task = resolve.bulk_query_a(ip2domainList)  # 解析域名地址A记录
        resolvedomain2IpList = loop.run_until_complete(task)
        for _ in resolvedomain2IpList:
            self.ipList.append(_['ip'])
        self.ipList = list(set(self.ipList))
        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[4]
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
        gLogger.info("Ip2domainSpider Start")
        global gDomainList
        self.ipList = [i for i in self.ipList if i != '']  # 清洗一遍，这里面可能存在一个''，空字符串
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        ip2domainSpider = Ip2domainSpider(self.domain, self.ipList)
        resList = loop.run_until_complete(ip2domainSpider.main())
        self.lock.acquire()
        gDomainList.extend(resList)
        gDomainList = list(set(gDomainList))
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
        gLogger.info("PortSpider Start")
        global gIpPortServiceList
        portscan = PortScan(self.domain, self.ipPortList)
        loop = asyncio.get_event_loop()
        gIpPortServiceList, httpList = loop.run_until_complete(portscan.main())
        self.lock.acquire()
        gDomainList.extend(httpList)
        self.lock.release()

    # 存活探测，限制并发数
    def aliveSpider(self):
        def saveWebParamsList(domain, webParamsList):
            workbook = openpyxl.load_workbook(abs_path + str(domain) + ".xlsx")
            worksheet = workbook.worksheets[8]
            index = 0
            while index < len(webParamsList):
                web = list()
                web.append(webParamsList[index])
                worksheet.append(web)
                index += 1
            workbook.save(abs_path + str(domain) + ".xlsx")
            workbook.close()

        gLogger.info("AliveSpider Start")
        global gDomainList, gWebParamsList, gDomainAliveList
        pbar = tqdm(total=len(gDomainList), desc='[{}]'.format('AliveSpider'), ncols=100)
        aliveSpider = AliveSpider(self.domain, gDomainList, pbar)
        loop = asyncio.get_event_loop()
        gWebParamsList, gDomainAliveList = loop.run_until_complete(aliveSpider.main())
        saveWebParamsList(self.domain, gWebParamsList)

    # main start
    def run(self):
        # 检查cdn @author ske(大师兄)
        def checkCdn(domain):
            gLogger.info("CheckCdn start")
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
        def flushIpSegment(domain, ipList, ipSegmentList):
            tempIpSegmentList = getIpSegment(ipList)
            for ipSegment in tempIpSegmentList:
                ipSegmentList.append({'ipSegment': ipSegment, 'ip': [], 'num': 0})
            for ip in ipList:
                for ipSegment in tempIpSegmentList:
                    ipList = IP(ipSegment)
                    for i in ipList:
                        if str(ip) == str(i):
                            for j in ipSegmentList:
                                if j.get('ipSegment') == ipSegment:
                                    j['num'] += 1
                                    j['ip'].append(ip)
            workbook = openpyxl.load_workbook(abs_path + str(domain) + ".xlsx")
            worksheet = workbook.worksheets[5]
            index = 0
            while index < len(ipSegmentList):
                web = list()
                web.append(ipSegmentList[index]['ipSegment'])
                web.append(str(ipSegmentList[index]['ip']))
                web.append(ipSegmentList[index]['num'])
                worksheet.append(web)
                index += 1
            workbook.save(abs_path + str(domain) + ".xlsx")
            workbook.close()

        def flushAsn(domain, asnList):
            workbook = openpyxl.load_workbook(abs_path + str(domain) + ".xlsx")
            worksheet = workbook.worksheets[6]
            index = 0
            while index < len(asnList):
                web = list()
                web.append(asnList[index])
                worksheet.append(web)
                index += 1
            workbook.save(abs_path + str(domain) + ".xlsx")
            workbook.close()

        # 相似度匹配
        def getSimilarityMatch(domain, domainList):
            # 比如azxc.com域名
            # admin.xxx.azxc.com oka.xxx.azxc.com test.a-xwow.azxc.com test.w-xwow.azxc.com
            # 其中 admin.ds.azxc.com oka.da.azxc.com 和  test.a-xwow.azxc.com test.w-xwow.azxc.com 这两对就是匹配的
            # 结果为如下:
            # generate admin.FUZZ.azxc.com
            # test.FUZZ-xwow.azxc.com
            gLogger.info("DomainSimilarityMatch start")
            resList = []
            newDomainList = [i for i in domainList if domain in i]
            domainIndex = 0
            while domainIndex < len(newDomainList):
                current = newDomainList[domainIndex]
                goodIndexList = MyDifflib.getCloseMatchIndex(current, newDomainList, n=10000, cutoff=0.8)
                currentResultList = []
                for index in reversed(sorted(goodIndexList)):
                    currentResultList.append(newDomainList[index])
                    # if current in domainList[index]:
                    del newDomainList[index]
                resList.append(currentResultList)
                domainIndex += 1
            workbook = openpyxl.load_workbook(abs_path + str(domain) + ".xlsx")
            worksheet = workbook.worksheets[16]
            index = 0
            while index < len(resList):
                web = list()
                web.append(str(resList[index]))
                worksheet.append(web)
                index += 1
            workbook.save(abs_path + str(domain) + ".xlsx")
            workbook.close()

        global gDomainList, gDomainAliveList, gIpPortServiceList, gWebParamsList

        # -----------------------

        # 0、备案查询
        # self.beianSpider()

        # 1、checkCdn
        # checkCdn(self.domain)

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
        self.threadList.append(Thread(target=self.baiduSpider, ))
        self.threadList.append(Thread(target=self.bingSpider, ))
        self.threadList.append(Thread(target=self.ctfrSpider, ))
        self.threadList.append(Thread(target=self.netSpider, ))
        self.threadList.append(Thread(target=self.githubSpider, ))
        for _ in self.threadList:
            _.start()
        for _ in self.threadList:
            _.join()

        # 5、清洗整理数据
        # self.flushResult()

        # 6、友链爬取
        self.friendChainsSpider()

        # 7、domain2ip
        # self.domain2ip()

        # 8、ip2domain
        # self.ip2domain()

        # 9、sslSpider @keefe @行牛 @ske 2021.09.01 SSL
        # self.sslSpider()

        # 10、alive
        self.aliveSpider()

        # 11、asn和ip段整理
        # flushIpSegment(self.domain, self.ipList, self.ipSegmentList)
        # flushAsn(self.domain, self.asnList)

        # 12、过滤属于CDN网段的IP
        # filterCDN()

        # 13、port scan in self.ipPortList
        # print('portConfig: ', portConfig)
        # portConfig = GlobalVariableManager.getValue('portConfig')
        # PortWrapper.generatePorts(portConfig, self.ipPortList)
        # self.ipPortSpider()

        # 14、去重子域名
        gDomainList = list(set(gDomainList))

        # 15、可探测FUZZ收集
        getSimilarityMatch(self.domain, gDomainList)

        print('==========================')
        gLogger.info('[+] [AsnList] [{}] {}'.format(len(self.asnList), self.asnList))
        print('==========================')
        gLogger.info('[+] [IpList] [{}] {}'.format(len(self.ipList), self.ipList))
        print('==========================')
        gLogger.info('[+] [IpSegmentList] [{}] {}'.format(len(self.ipSegmentList), self.ipSegmentList))
        print('==========================')
        gLogger.info('[+] [IpPortList] [{}] {}'.format(len(self.ipPortList), self.ipPortList))
        print('==========================')
        gLogger.info('[+] [JavaScriptParamsList] [{}] {}'.format(len(self.javaScriptParamList), self.javaScriptParamList))
        print('==========================')
        gLogger.info('[+] [gWebParamsList] [{}] {}'.format(len(gWebParamsList), gWebParamsList))
        print('==========================')
        gLogger.info('[+] [gIpPortServiceList] [{}] {}'.format(len(gIpPortServiceList), gIpPortServiceList))
        print('==========================')
        gLogger.info('[+] [gDomainList] [{}] {}'.format(len(gDomainList), gDomainList))
        print('==========================')
        gLogger.info('[+] [gDomainAliveList] [{}] {}'.format(len(gDomainAliveList), gDomainAliveList))
        exit(0)

# Exploit
class Exploit(object):
    def __init__(self, domain):
        self.threadList = []
        self.domain = domain

    def AliveScan(self):
        pass
        # AliveScan(self.domain, self.domainList).main()

    def UnauthPortScan(self):
        pass
        # global gDomainList
        # # [{"subdomain": "www.zjhu.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        # queue = asyncio.Queue(-1)
        # for aTask in gDomainList:
        #     aIp = aTask.get('ip')
        #     aPortList = aTask.get('port')
        #     for port in aPortList:
        #         queue.put("{}:{}".format(aIp, port))  # IP+端口, 接下里就是异步socket探测banner来进行相关利用即可.
        # IpUnauth(self.domain, queue).main()

    def unauthLeakHttpScan(self):
        pass
        # HttpUnauth(self.domain, self.domainList).main()

    def jsExploit(self):
        # SqlScan(self.domain, self.clear_task_list).main()
        pass

    # 基于网站参数的漏扫
    def sqlExploit(self, webParamsList):
        gLogger.info('SqlScan Start')
        # queue = asyncio.Queue(-1)
        # for aTask in webParamsList:
        #     pass
        #     queue.put("{}:{}".format(aIp, port))  # IP+端口, 接下里就是异步socket探测banner来进行相关利用即可.
        # IpUnauth(self.domain, queue).main()

    # 基于网站框架的漏扫
    def webExploit(self, domainList):
        gLogger.info('CmsScan Start')
        moduleLoader = ModuleLoader('exploit')
        moduleList = moduleLoader.moduleLoad(moduleType='exploit')
        cmsScan = CmsScan(self.domain, domainList, moduleList)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cmsScan.main())
        # queue = asyncio.Queue(-1)
        # for aTask in self.domainList:
        #     aIp = aTask.get('ip')
        #     aPortList = aTask.get('port')
        #     for port in aPortList:
        #         queue.put("{}:{}".format(aIp, port))  # IP+端口, 接下里就是异步socket探测banner来进行相关利用即可.
        # IpUnauth(self.domain, queue).main()

    # 基于端口服务的漏扫
    def serviceExploit(self, ipPortServiceList):
        gLogger.info('ServiceScan Start')
        total = 0
        for targetService in ipPortServiceList:
            total += len(targetService['ip'])
        pbar = tqdm(total=total, desc="ServiceScan", ncols=100)  # total是总数
        servicescan = PortServiceScan(self.domain, ipPortServiceList, pbar)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(servicescan.main())

    def run(self):
        global gDomainAliveList, gIpPortServiceList, gWebParamsList
        # webExp
        self.webExploit(gDomainAliveList)
        self.serviceExploit(gIpPortServiceList)
        self.sqlExploit(gWebParamsList)

        # serviceExp
        # self.serviceExploit()
        # sqlExp
        # self.sqlExploit()

        # for i in self.threadList:
        #     i.start()
        #
        # for i in self.threadList:
        #     i.join()


def getVersion():
    return 'Myscan Tool\'s version is 2.0 - HengGe'


def parse_args():
    parser = argparse.ArgumentParser(prog='MyScan', description='The tool is beneficial to attack web/service')
    parser.add_argument('-u', '--url', type=str, help='a url. for example: -u zjhu.edu.cn')
    parser.add_argument('-d', '--domain', type=str, help='Target domain. for example: -d zjhu.edu.cn')
    parser.add_argument('-cn', '--company', type=str, help='Target company. for example: -cn 横戈信息安全有限公司')
    parser.add_argument('-i', '--ips', type=str,
                        help='Target ip. for example: -i 192.168.1.1-192.168.1.127,192.168.3.1-192.168.3.255 | 192.168.1.0/24,192.168.3.0/24 | 192.168.1.1,192.168.1.2')
    parser.add_argument('-p', '--port', type=str, default='top100',
                        help='Every Ip port, default top100, for example: -p top100')
    parser.add_argument('-m', '--module', type=str,
                        help='Load/Show Payload Module(exploit/third/all)，example: -m exploit')
    parser.add_argument('-f', '--file', type=str, help='a file')
    parser.add_argument('-fs', '--fofa', type=str, help='fofa scan title. for example: -fs "domain=\"zjhu.edu.cn\"')
    parser.add_argument('-ss', '--serviceScan', action='store_true', help='for service scan.')
    parser.add_argument('-cs', '--cmsScan', action='store_true', help='for cms scan.')
    parser.add_argument('-x', '--proxy', help='http proxy')
    parser.add_argument('-v', '--version', action='version', version=getVersion(), help='Display version')
    # parser.add_argument('-f', '--file', type=str, help='file')
    return parser.parse_args()


if __name__ == '__main__':
    print('[+] Welcome From HengGe\'s Team ^.^')
    GlobalVariableManager.init()
    starttime = time.time()
    args = parse_args()
    if args.domain:
        if args.company:
            companySpider = CompanyStructSpider(args.domain, args.company)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(companySpider.main())
            print("[+] 总花费时间: " + str(time.time() - starttime))
            exit(0)
        if not os.path.exists(abs_path + args.domain + ".xlsx"):
            if args.port:
                GlobalVariableManager.setValue('portConfig', args.port)
            createXlsx(args.domain)
            spider = Spider(args.domain)
            spider.run()
            exploit = Exploit(args.domain)
            exploit.run()
            print("[+] 总花费时间: " + str(time.time() - starttime))
            exit(0)
        else:
            exit('[-] 文件名{}已存在，如果要运行的话需要将该文件{}.xlsx改名或者删除.'.format(args.domain, args.domain))
    if args.cmsscan:
        if args.url:
            moduleLoader = ModuleLoader('exploit')
            if args.module is None:
                print('[+] load all module')
                moduleList = moduleLoader.moduleLoad(moduleType='exploit')
            else:
                print('[+] load module -> {}'.format(args.module.split(',')))
                modulenameList = args.module.split(',')
                if len(modulenameList) == 1:
                    moduleList = moduleLoader.moduleLoad(moduleType='exploit', moduleObject=args.module)
                else:
                    moduleList = moduleLoader.moduleLoad(moduleType='exploit', moduleObject=modulenameList)
                if not moduleList:
                    exit(0)
            loop = asyncio.get_event_loop()
            domainList = [args.url]
            cmsScan = CmsScan('result.com', domainList, moduleList)
            loop.run_until_complete(cmsScan.main())
            print("[+] 总花费时间: " + str(time.time() - starttime))
            exit(0)
        if args.fofa:
            moduleLoader = ModuleLoader('exploit')
            if args.module is None:
                print('[+] load all module')
                moduleList = moduleLoader.moduleLoad(moduleType='exploit')
            else:
                print('[+] load module -> {}'.format(args.module.split(',')))
                modulenameList = args.module.split(',')
                if len(modulenameList) == 1:
                    moduleList = moduleLoader.moduleLoad(moduleType='exploit', moduleObject=args.module)
                else:
                    moduleList = moduleLoader.moduleLoad(moduleType='exploit', moduleObject=modulenameList)
                if not moduleList:
                    exit(0)
            try:
                from core.api import MyNetApi
                # from core.api import MyNetApi.MyNetApi.fofaSearch()
            except ImportError:
                exit('[-] Import Error from core.api import MyNetApi error')
            loop = asyncio.get_event_loop()
            domainList = loop.run_until_complete(MyNetApi.fofaSearch(args.fofa))
            cmsScan = CmsScan('result.com', domainList, moduleList)
            loop.run_until_complete(cmsScan.main())
            print("[+] 总花费时间: " + str(time.time() - starttime))
            exit(0)
    # servicescan + portscan
    if args.servicescan:
        if args.ips:
            ipPortList = PortWrapper.generateFormat(args.ips)
            PortWrapper.generatePorts(args.port, ipPortList)
            portscan = PortScan('result.com', ipPortList)
            loop = asyncio.get_event_loop()
            ipPortServiceList, httpList = loop.run_until_complete(portscan.main())
            total = 0
            for targetService in ipPortServiceList:
                total += len(targetService['ip'])
            pbar = tqdm(total=total, desc="ServiceScan", ncols=100)  # total是总数
            servicescan = PortServiceScan('result.com', ipPortServiceList, pbar)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(servicescan.main())
            print("[+] 总花费时间: " + str(time.time() - starttime))
            exit(0)
        else:
            exit('[-] 输入要进行服务扫描的IP')
    # 单独端口扫描选择
    if args.ips:
        # 生成ipPortList格式
        ipPortList = PortWrapper.generateFormat(args.ips)
        # 对ipPortList中的ip进行对应的端口填充
        PortWrapper.generatePorts(args.port, ipPortList)
        portscan = PortScan('result.com', ipPortList)
        loop = asyncio.get_event_loop()
        ipPortServiceList, httpList = loop.run_until_complete(portscan.main())
        print("==================Service========================")
        gLogger.info(ipPortServiceList)
        print("==================HTTP========================")
        gLogger.info(httpList)
        print("[+] 总花费时间: " + str(time.time() - starttime))
        exit(0)
    if args.module and args.domain is None:
        ModuleLoader.showModule(args.module)
        # cmsScan = CmsScan('result.com', domainList, moduleList)
        exit(0)
    # if domain and module is None:
    #     if not os.path.exists(abs_path + domain + ".xlsx"):
    #         createXlsx(args.domain)
    #         spider = Spider(args.domain)
    #         domainList, ipPortServiceList, webParamsList = spider.run()
    #         # exploit = Exploit(args.domain, domainList, ipPortServiceList, webParamsList)
    #         # exploit.run()
    #     else:
    #         exit('文件{}.xlsx已存在，如果要运行的话需要将该文件{}.xlsx改名或者删除.'.format(args.domain, args.domain))
    # elif module and domain is None:
    #     ModuleLoader.showModule(module)
    # elif domain is not None and module is not None:
    #     print(domain, module)

    # print(globals())
    # # g_portregisterType = args.
    # if args.domain:
    #     if not os.path.exists(abs_path + args.domain + ".xlsx"):
    #         createXlsx(args.domain)
    #         spider = Spider(args.domain)
    #         domainList, ipPortServiceList, webParamsList = spider.run()
    #         exploit = Exploit(args.domain, domainList, ipPortServiceList, webParamsList)
    #         exploit.run()
    #     else:
    #         print('文件{}.xlsx已存在，如果要运行的话需要将该文件{}.xlsx改名或者删除.'.format(args.domain, args.domain))

    # record test something , for example Exploit Module
    # domainList, ipPortServiceList, webParamsList = ['61.189.45.122:8080', '218.86.35.162:8081', '220.163.130.150:88', '218.247.22.126:8080', '116.24.102.179:88', '222.88.105.19:443', '62.234.128.52:9001', '60.10.197.58:8181', '122.227.172.118:443', '60.247.78.102:443', '60.12.210.108:443', '59.120.193.242', '222.66.40.18:443', '47.100.207.131:8080', '218.32.202.243', '211.20.130.93:443', '211.21.133.102:443', '125.227.194.149', '1.34.121.139', '111.7.82.30', '47.95.241.106:8080', '221.176.253.229', '61.178.243.56:1080', '62.234.128.52:9002', '220.130.178.183:8080', '220.130.178.183', '218.32.202.243:8080', '60.248.32.155:443', '60.251.22.220:443', '211.20.130.93', '222.66.40.20:443', '106.14.170.151:443', '59.120.193.242:443', '61.219.197.219', '220.135.17.43', '61.178.55.205:443', '27.223.15.116:8081', '116.24.101.179:88', '202.110.190.163', '222.175.7.225:443', '58.221.135.158:88', '219.87.163.219:8080', '1.85.53.170:8081', '125.45.237.208:18080', '222.180.68.39:443', '119.39.5.251:443', '122.227.172.118:82', '222.180.68.39:8081', 'v2.amassvip.com:18080', '113.70.57.189:6666', '123.127.61.175:8081', '222.175.7.225:8082', '106.37.229.62:8080', 'https://221.215.1.134', '222.184.102.46:8001', '182.92.211.196:8080', '60.205.143.140:443', '49.5.12.140:443', '119.136.19.252:88', '61.30.98.100:8080', '182.106.236.228:8081', '218.4.66.139:8080', '218.245.1.8', '222.168.37.70:443', 'www.crownpo.com', '222.180.68.39:8084', '116.24.103.42:88', '115.159.46.127:8080', '119.136.19.254:88', '58.213.46.154:18080', '1.202.137.77:8000', '183.247.173.122:8082', '60.191.118.211:8080', '220.231.134.114:8888', '211.72.53.141', '218.86.35.162:81', '221.229.247.188:8080', '106.14.170.151:8080', '120.221.150.9:8081', '111.47.28.113:9090', '221.214.10.132:8088', '117.141.32.79:8081', '218.245.1.8:443', '123.127.61.175:9000', '58.213.109.125:8880', '58.213.109.123:8888', '218.240.147.175:8080', '112.125.88.205:8080', '124.167.244.118', '60.250.128.205:8080', '123.232.116.55:8080', '61.130.100.220', '61.222.32.214:8080', '60.211.185.198:8080', '211.72.53.141:8080', '58.208.60.166:8080', '58.56.96.181:18080', '220.178.74.178:8080', '183.136.222.90:8080', '58.218.199.15:8080', '221.226.215.108:18080', '122.227.172.118:8082', '222.76.213.236:8080', '222.76.213.236:8000', '218.65.236.14:8088', '124.115.214.85:18000', '115.159.46.127:8443', '60.247.78.102:8080', '61.157.184.136:8080', '183.62.203.115:8080', '47.92.253.130:8088', '61.144.203.36:88', '182.106.236.228:81', '112.125.88.205', '111.207.218.6:8080', '60.208.61.36:8443', '222.92.143.50:8081', '1.34.121.139:8080', '116.247.103.211:8080', '124.130.131.92:443', '110.86.4.118:8888', '60.251.22.220:8080', '58.213.109.125:8888', '220.231.134.114:443', '122.228.226.68:8080', '115.57.0.14:443', '220.246.55.241', '58.221.172.61:18181', '211.20.130.93:8080', '47.101.59.86:8080', '61.139.77.80:8080', '218.88.150.167', '221.226.253.38:18080', '210.61.217.109:8080', '60.216.53.165:8081', '121.40.195.34:8082', '47.100.212.202', '61.178.55.205:8080', '27.154.239.154:8888', '139.196.27.79:8080', '124.67.165.199:2002', '113.128.218.221:8081', '139.196.27.79', '58.56.103.106:9090', '47.100.212.202:8080', '219.148.50.35:8443', '222.180.68.39:8086', '222.180.68.39:8087', '59.120.193.242:8080', '125.46.31.44:18080', '58.59.48.150:8081', '221.214.10.132:8081', '218.3.161.2:8080', '49.5.12.140:8080', '122.224.110.54:18080', '61.175.247.254:18080', '111.11.148.41', '113.128.218.220:8443', '218.22.207.110:18080', '61.185.105.162:8081', '220.246.55.241:8080', '61.185.18.36:8080', '61.219.197.219:8080', '183.62.157.67:8080', '60.30.137.38:8888', '123.151.172.130:88', '58.246.67.38:8080', '58.22.29.148:18080', '118.31.3.77:8080', '220.246.55.241:443', '58.250.41.20:8081', '47.96.28.132:443', '119.39.5.251:9090', '123.138.108.133:443', '59.125.177.169', '47.100.207.131', '47.101.59.86', '210.21.36.142:8080', '1.202.30.86', '219.87.163.219', '60.248.32.155', '61.185.18.36', '218.29.110.28:443', '61.178.55.205', '61.30.98.100', '122.224.110.54', '39.105.1.174', '221.238.47.226:443', '39.104.24.138:8082', '125.227.194.149:8080', '220.135.17.43:8080', '119.3.178.106:8080', '118.122.120.4:9999', '222.88.105.19:18080', '222.180.68.39:8099', '59.125.177.169:8080', '113.70.59.152:6666', '117.67.159.203:9999', '58.250.41.14:8081', '218.63.200.3:8081', '47.92.73.254:8080', '111.207.115.226:8000', '58.56.103.106:9999', '111.207.218.6', '47.96.28.132:8090', '117.67.223.11:9999', '120.101.196.4:8080', '112.2.58.229:81', '36.110.90.6:8000', '219.148.50.35:8002', '60.208.61.36:18080', '39.104.24.138:443', '222.73.197.21:8080', '1.202.137.77:8080', '60.191.185.86:8080', '123.233.120.138:18080', '111.11.148.41:443', '154.92.14.206', '218.247.22.126', '220.162.157.182:86', '106.46.77.61:8888', '60.208.61.35:18080', '221.229.247.188', '222.184.102.46:8002', '115.57.0.14:9090', '218.63.200.3:3000', '222.180.68.39:5222', '120.209.186.106:18080', '116.247.103.211', '60.13.3.24:8080', '59.56.54.41:8888', '117.68.254.233:9999', '222.88.105.19:8080', '218.29.12.202:18080', '123.232.116.55:443', '61.142.246.118:18080', '118.31.3.77:443', '110.86.4.118:8443', '124.88.160.66:8888', '60.13.183.172:8090', '120.36.155.52', '123.151.172.130:8888', '220.167.54.10:8888', '60.216.101.147:8081', '113.196.136.196:443', '221.176.253.229:8080', '58.56.96.181:443', '60.191.118.211:443', '219.233.192.161:443', '118.122.120.4:9090', '111.207.218.6:443', '220.130.178.183:443', '58.246.6.117:85', '115.57.0.14:9999', '39.105.1.174:444', '125.46.31.44:443', '203.86.8.155:18080', '61.156.217.52:18080', '218.3.95.121:88', '222.180.1.42:88', '116.247.122.18:8080', '154.92.14.206:8080', '218.65.236.14:18080', '47.95.241.106', '220.231.134.114:8080', '203.86.8.155:443', '113.128.218.221:8443', '58.213.159.156:83', '222.190.116.172:8888', '222.135.186.250:9090', '183.224.118.165:8081', '180.140.243.207:18080', '60.208.61.35:8443', '59.110.159.144:30001', '113.70.56.55:7777', '59.56.54.227:8888', '60.247.78.102', '183.203.222.141:443', '47.95.241.106:443'], [], []
    # exploit = Exploit('zjhu.edu.cn', domainList, ipPortServiceList, webParamsList)
    # exploit.run()
