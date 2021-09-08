# coding=utf-8

from core.MyModuleLoader import *
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
# from spider.ParamLinkSpider import *
from spider.FriendChainsSpider import *
from spider.StructSpider import *
from spider.AliveSpider import *

from common import resolve

# from exploit.AliveScan import *
# from exploit.IpUnauthExploit import *
# from exploit.HttpUnauthExploit import *
from exploit.CmsExploit import *
from exploit.SQLExploit import *
from exploit.ServiceExploit import *

from threading import Thread

import os
import argparse
import time
import sys
import asyncio
import importlib
from IPy import IP

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

abs_path = os.getcwd() + os.path.sep  # 路径
thirdLib = abs_path + 'spider/thirdLib/'
exploitLib = abs_path + 'exploit/web/'

gIpSegmentList = []  # 存储资产IP区段分布以及资产IP在指定的区段出现的次数  [{"111.111.111.0/24":1},{"111.111.222.0/24":1}]
gAsnList = []  # ASN记录
gIpList = []  # 用来统计gIpSegmentDict
gIpPortList = []  # 存储端口+服务
gTopDomainList = []  # 存储顶级域名记录 @ske
gPortRegister = []  # 存储用于portSpider模块中要扫描的端口


# Spider
class Spider(object):
    def __init__(self, domain):
        self.domain = domain  # 要爬取的域名
        self.threadList = []  # 线程启动列表
        self.domainList = []  # 用来存储所有匹配到的子域名和一些隐形资产
        self.ipPortServiceList = []
        self.webParamsList = []  # 存储可注入探测参数列表 ["http://www.baidu.com/?id=1111*"]
        self.javaScriptParamList = []  # 存储js文件中的js敏感接口 @小洲师傅
        self.clearTaskList = []  # 存储整理过后的域名 [{"subdomain": "www.zjhu.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        self.lock = threading.Lock()
        # self.moduleLoader = ModuleLoader()

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
        thirdModuleList = filter(lambda x: (True, False)[x[-3:] == 'pyc' or x[-5:] == '__.py' or x[:2] == '__'],
                           os.listdir(thirdLib))

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
        global gAsnList, gIpList, gIpPortList
        net = NetSpider(self.domain)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(net.main())
        resList, gAsnList, gIpList, gIpPortList = loop.run_until_complete(t)
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
        global gIpPortList
        portscan = PortScan(self.domain, gIpPortList, gPortRegister)
        loop = asyncio.get_event_loop()
        self.ipPortServiceList, httpList = loop.run_until_complete(portscan.main())
        self.lock.acquire()
        self.domainList.extend(httpList)
        self.lock.release()

    # 存活探测，限制并发数
    def aliveSpider(self):
        logging.info("aliveSpider Start")
        aliveSpider = AliveSpider(self.domain, self.domainList)
        loop = asyncio.get_event_loop()
        resList = loop.run_until_complete(aliveSpider.main())
        self.lock.acquire()
        self.webParamsList.extend(resList)
        self.lock.release()

    # main start
    def run(self):
        # 检查cdn @author ske(大师兄)
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

        global gAsnList, gIpList, gIpSegmentList, gIpPortList

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

        # 9、sslSpider @keefe @行牛 @ske 2021.09.01 SSL
        # self.sslSpider()

        # 10、alive
        self.aliveSpider()

        # 11、asn和ip段整理
        flushIpSegment(self.domain)
        flushAsn(self.domain)

        # 12、过滤属于CDN网段的IP

        # 13、port scan in self.ipPortList
        self.ipPortSpider()

        # 去重子域名
        self.domainList = list(set(self.domainList))
        print("=============")
        print('[+] [gAsnList] [{}] {}'.format(len(gAsnList), gAsnList))
        print("=============")
        print('[+] [gIpList] [{}] {}'.format(len(gIpList), gIpList))
        print("=============")
        print('[+] [gIpSegmentList] [{}] {}'.format(len(gIpSegmentList), gIpSegmentList))
        print("=============")
        print('[+] [ipPortList] [{}] {}'.format(len(gIpPortList), gIpPortList))
        print("=============")
        print('[+] [paramsList] [{}] {}'.format(len(self.webParamsList), self.webParamsList))
        print("=============")
        print('[+] [javaScriptParamsList] [{}] {}'.format(len(self.javaScriptParamList), self.javaScriptParamList))
        print("=============")
        print('[+] [ipPortServiceList] [{}] {}'.format(len(self.ipPortServiceList), self.ipPortServiceList))
        print("=============")
        print('[+] [domainList] [{}] {}'.format(len(self.domainList), self.domainList))
        # 最后返回处理好的数据 交给Exploit类
        return self.domainList, self.ipPortServiceList, self.webParamsList


# Exploit
class Exploit(object):
    def __init__(self, domain, domainList, ipPortServiceList, webParamsList):
        self.threadList = list()
        self.domain = domain
        self.domainList = domainList
        self.ipPortServiceList = ipPortServiceList
        self.webParamsList = webParamsList

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
        # IpUnauth(self.domain, queue).main()

    def unauthLeakHttpScan(self):
        pass
        # HttpUnauth(self.domain, self.domainList).main()

    def jsExploit(self):
        # SqlScan(self.domain, self.clear_task_list).main()
        pass

    # 基于网站参数的漏扫
    def sqlExploit(self):
        logging.info("SqlScan Start")
        global gParamsList
        queue = asyncio.Queue(-1)
        for aTask in gParamsList:
            pass
        #     queue.put("{}:{}".format(aIp, port))  # IP+端口, 接下里就是异步socket探测banner来进行相关利用即可.
        # IpUnauth(self.domain, queue).main()

    # 基于网站框架的漏扫
    def webExploit(self):
        logging.info("CmsScan Start")
        moduleLoader = ModuleLoader(exploitLib, 'Script')
        moduleList = moduleLoader.defaultModuleLoad('exploit')
        cmsScan = CmsScan(self.domain, self.domainList, moduleList)
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
    def serviceExploit(self):
        logging.info("ServiceScan Start")
        total = 0
        for targetService in self.ipPortServiceList:
            total += len(targetService['ip'])
        pbar = tqdm(total=total, desc="ServiceScan", ncols=150)  # total是总数
        servicescan = PortServiceScan(self.domain, self.ipPortServiceList, pbar)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(servicescan.main())

    def run(self):
        def init():
            pass

        # self.thread_list.append(Thread(target=self.AliveScan))
        # self.thread_list.append(Thread(target=self.CmsScan))  # cms/框架扫描
        # self.thread_list.append(Thread(target=self.IpUnauthScan))  # 未授权扫描ip
        # self.thread_list.append(Thread(target=self.HttpUnauthScan))  # 未授权扫描http域名
        # self.thread_list.append(Thread(target=self.SqlScan)) # SQL注入扫描

        # webExp
        self.webExploit()
        # serviceExp
        # self.serviceExploit()
        # sqlExp
        # self.sqlExploit()

        # for i in self.threadList:
        #     i.start()
        #
        # for i in self.threadList:
        #     i.join()


def parse_args():
    parser = argparse.ArgumentParser(prog='MyScan', )
    parser.add_argument('-d', '--domain', type=str, required=True, help="Target domain.")
    parser.add_argument('-f', '--fofa', type=str, help='fofa scan title. for example title=""')
    parser.add_argument('-p', '--scanport', type=str, help='will all port scan in subdomain.')
    parser.add_argument('-c', '--csegment', type=str, help='csegment. for example 192.168.1.0/24')
    parser.add_argument('-v', '--version', type=str, help='%(prog)s v2')
    return parser.parse_args()


if __name__ == '__main__':
    # print('''
    #     Come From HengGe's Team ^.^
    # ''')
    # starttime = time.time()
    # args = parse_args()
    # g_domain = args.domain
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
    # print("总共耗时时间为：" + str(time.time() - starttime))

    domainList, ipPortServiceList, webParamsList = ['111.33.16.58:9999', '58.37.56.233:8099', 'https://113.247.230.165', 'https://117.25.175.221', '120.205.6.238:8020', 'https://nanjing.zbj.com', 'report.etoonpack.net', 'https://182.92.6.224', '157.0.141.5:8002', 'https://59.49.12.147', 'doc.fanruan.com', '47.74.34.81:8090', 'oa.t3c.com.cn:8080', 'https://scd7a6b5c4a5-sb-qn.qiqiuyun.net', 'https://www.xuetuwuyou.com', 'scd7a6b5c4a5-sb-qn.qiqiuyun.net', 'https://180.76.181.218', 'crm.uniworld-sz.cn', '129.226.11.85:8002', '222.92.23.58:8002', 'https://www.fangwenw.com', 'https://115.159.81.227', '14.238.11.22', 'https://www.riskivy.com', 'dler.org', 'www.dler.org', '113.196.127.201', 'https://www.deepexi.com', 'www.dxm.so', 'https://shop.zbj.com', 'https://39.108.26.127', 'jx.jdjob88.com', '0930.job1001.com', '0932.job1001.com', 'gs.job1001.com', '0760.job1001.com', '0762.job1001.com', 'https://help.finereport.com', 'https://47.105.75.115', 'https://120.55.182.129', 'https://120.55.63.30', '121.40.62.70:8080', '219.235.224.163', 'www.teemlink.com', '120.53.241.136:8082', 'https://vtzw.com', 'xqoffice.cn', '182.61.4.173:8081', 'www.acleus.com', '39.101.162.129:8080', '203.79.1.26:8080', 'https://jishu88.net', 'https://121.42.175.55', '157.122.176.68:8080', '52.83.146.238:8002', '39.89.249.206:8088', '0511.job1001.com', '0519.job1001.com', '0512.job1001.com', 'https://beijing.zbj.com', '221.10.231.228:8088', 'itsx.com.cn', 'www.itsx.com.cn', '47.106.197.158:8093', '39.101.162.129:3389', '47.112.115.192', 'www.telwing.com', '218.64.66.55:8080', 'https://gztk.zbj.com', '123.160.223.8:21', '139.196.113.208', '210.123.136.144', 'https://112.74.14.140', 'https://124.251.118.32', '116.227.238.110:9100', 'https://119.254.81.101', 'https://www.escco.co.jp', 'https://1.33.171.100', 'www.jisuxz.com', 'https://www.yotopic.com', 'https://47.103.83.124', '59.63.163.216:8080', 'https://wiki.96.mk', '39.99.234.9:8080', '39.100.85.100:8001', '39.107.236.254:445', '157.0.141.2:8002', 'https://fanruan.butian.net', '112.25.133.50:8002', 'https://129.204.47.157', 'https://www.tangyuecan.com', 'https://118.31.40.140', '118.190.78.32:8080', 'https://103.40.192.202', 'bi.jingda.cn', '218.4.217.244:161', 'www.tzcpzs.com:88', '118.31.247.126:9000', 'bbs.llinfo.com.cn', 'https://zy.zbj.com', 'https://yx.zbj.com', 'https://bd.zbj.com', 'https://dasai.zbj.com', 'https://zx.zbj.com', 'https://sw.zbj.com', 'https://jinshi.zbj.com', 'https://search.zbj.com', 'https://zp.zbj.com', 'https://88.zbj.com', 'https://qf.zbj.com', 'https://toutiao.zbj.com', 'https://cy.zbj.com', 'https://hy.zbj.com', 'https://work.zbj.com', 'https://task.zbj.com', 'https://xue.zbj.com', 'https://yichang.zbj.com', 'https://rule.zbj.com', 'https://cdn.hellobi.com', 'https://58.49.97.221', 'https://huaxiacloud.com', 'www.xzappw.cn', 'https://wuhai.zbj.com', 'sw.job1001.com', '116.227.236.162:9100', '14.221.4.167:8888', 'https://industry.zbj.com', '121.40.95.104:9090', '180.76.47.208:5050', '119.3.149.98:8080', '121.40.102.183:8888', '109.244.32.36', 'https://35.234.18.36', '210.22.142.102', 'www.biozonn.com:5678', '121.36.146.133:8888', '114.116.25.167:9001', '52.83.146.238:8001', 'www.xtshws.com', 'https://54.223.78.35', 'https://114.215.152.129', 'market.yuntue.com', '39.108.156.243:8086', '47.104.192.2', '157.122.176.68:8088', '218.3.120.165:8002', '101.132.108.69:8080', '47.112.148.3:8000', 'https://yuchi.blog.csdn.net', '139.9.6.184:8080', '222.133.2.154:8088', 'bh.wzshjt.com:8888', '61.191.203.250:8890', '221.214.7.202:4040', 'https://119.180.26.213:8888', 'jimureport.com', 'www.jimureport.com', 'https://jeecg.blog.csdn.net', '139.224.239.143:8080', '139.196.85.42:8080', '111.85.88.32:8888', '183.60.97.155', 'blog.ajeelee.com', '222.89.107.84:8002', '47.101.151.18', '139.155.241.145', '113.102.205.33:8888', 'https://cloud.zbj.com', 'cloud.bdxzn.com', 'www.xuetuwuyou.com', '113.102.206.97:8888', '123.55.75.71:8060', '120.199.56.26:9090', 'https://shuzhiniao.com', 'https://market.fanruan.com', 'https://events.fanruan.com', 'https://www.fanruan.com', 'https://www.finereport.com', 'https://shop.finereport.com', '113.102.206.244:8888', '222.92.150.74:8002', '58.87.108.62:5678', 'https://guangzhou.zbj.com', 'https://www.dxm.so', 'https://twmarket.fanruan.com', 'https://fanruanbbs.obs.cn-east-2.myhuaweicloud.com', 'https://www.fanruansem.com', '120.79.234.50', '58.247.142.58:8888', '202.106.90.112', '58.210.96.153', 'www.cdjcow.com', '116.227.232.117:9100', 'www.fanruansem.com', 'finemaxdemo.fanruan.com', 'https://bbs.fanruan.com', 'fanruanbbs.obs.cn-east-2.myhuaweicloud.com', 'https://help.fanruan.com', '120.27.226.131:8000', '222.89.107.84:8001', 'https://go.zbj.com', '157.0.141.3:8002', '157.0.141.4:8002', 'r.huahai.net:8080', '218.4.138.125:8088', '120.55.182.129:8081', '47.89.22.215:8008', '106.38.10.199:8080', '114.116.159.82:4000', 'jisuxz.com', '59.47.54.83:3000', '218.65.71.94:8003', 'www.xyvrzb.com', '122.112.136.142:8888', '118.122.168.224:8088', 'xt12366.com', '139.155.174.239', '39.108.229.68:8000', '39.108.229.68:8000', '120.197.140.134:8888', '121.36.200.111:4000', 'https://116.62.166.24:8080', '61.186.131.77:135', '47.105.91.22', 'https://xuzhou.zbj.com', '180.166.206.186', 'www.xt12366.com', '116.6.116.58:8080', '180.168.135.131:9090', 'https://shenzhen.zbj.com', '58.247.80.2:8099', '218.71.141.22:8089', '218.206.186.144:8099', '49.234.137.31:3389', '0392.job1001.com', '0379.job1001.com', '0315.job1001.com', '0395.job1001.com', '0310.job1001.com', '58.210.216.117:8080', '47.242.239.244:3389', 'www.kaili365.net.cn:8080', 'https://opals-dev.dione.scoolaid.net', '39.108.229.68', '39.108.229.68:80', '125.46.12.154:8018', '219.142.82.174:9090', '218.93.228.69:8085', '119.23.188.184:80', '47.106.255.21:80', '106.15.58.131:80', '47.106.255.21:443', '47.106.254.114:443', 'hkcx.haxso.net', 'www.hkcx.com.cn', '0562.job1001.com', '0553.job1001.com', '0598.job1001.com', '222.134.79.4:7777', 'https://vul.sangyun.net', '112.124.31.29', '119.23.217.18', 'data.xaiu.edu.cn', 'pt.whfanzhou.com', '47.106.254.114:80', '60.191.75.218:18080', '61.164.65.98:8090', 'https://218.104.151.67', '1.117.189.135', 'https://59.56.228.110', '61.130.6.244', 'robot.finereport.com', 'dev.fanruan.com', '222.186.32.182:82', '106.14.187.184', 'https://www.edir.cc', '120.79.221.140', 'www.i4cu.xyz:8089', 'https://120.27.226.131', '122.224.53.165', '121.89.214.54', '58.210.216.117', 'https://research.fanruan.com', 'https://121.46.31.24', 'https://edu.fanruan.com', 'https://139.224.239.143', '115.236.75.118:10000', 'https://47.104.192.2', '112.90.146.203', '122.112.164.156', '221.199.40.76:9090', '221.3.236.79:8092', 'https://www.yunqifu.com', '120.55.23.61', '139.155.24.18', '222.190.117.5:8080', 'https://47.93.48.114', '116.236.30.66:8087', '61.136.141.137:8080', '140.246.129.176:8010', '183.230.42.232:8082', 'i4cu.xyz:8089', '120.27.226.131:8089', '47.95.194.117:8081', 'www.linkcreate.net', '106.14.157.183', '116.227.235.243:9100', 'dxm.so', 'https://39.100.110.91', 'https://220.189.231.219', '111.125.67.60:8088', 'https://139.9.6.184:8081', '77.242.240.147:3389', 'www.qljcgd.com:8899', 'www.agilesoft.cn', '122.237.100.48', 'https://www.mfsun.com', '106.15.58.131', '39.100.249.52', '1.15.27.179:5000', '220.171.1.35:8020', 'https://222.173.217.58:8888', 'report.tianfon.com', '106.15.45.188', '218.28.35.10:9090', '39.106.78.105', '218.107.193.34:8899', 'www.egunao.top', '222.75.177.149:9090', 'https://218.64.66.55', '124.128.201.160:8082', '218.90.161.37:8088', 'jackxiang.com', 'www.jackxiang.com', '60.190.20.213', '211.64.79.140', '123.173.79.72', '183.134.73.135', 'https://47.106.254.114', 'www.52geyou.com', 'https://119.23.217.18', '58.22.121.194:8800', '222.24.192.218', 'https://chongqing.zbj.com', 'https://tianjin.zbj.com', '119.254.227.144', 'hkcx.com.cn', '218.83.247.26', 'h.comoresolver.co', 'doc88.broadwaybuttz.co', '139.219.225.13:445', '8.135.19.36', 'https://opals.lloydminster.info', '47.96.13.236', 'https://106.52.105.147', 'www.chuanqi.press', 'https://www.chuanqi.press', 'https://101.32.74.142', '34.85.67.119:3389', '113.102.205.187:8888', 'https://124.251.111.171', '117.146.23.225:8082', 'https://xt12366.com', 'https://m.saiyu.com', 'https://www.saiyu.com', 'www.shuidong.cc', '14.221.4.23:8888', '39.100.110.91:8080', 'products.wk-china.com.cn', '42.247.33.5:8001', '111.30.108.184:8099', 'https://222.24.192.218', '116.236.32.218:88', '1.116.138.6', '47.105.187.236', '210.33.125.75', '120.55.63.30:8083', '91.201.4.69:3389', '120.40.39.194:8800', '121.5.141.210', '221.12.11.250:18080', '120.253.68.77:9090', '47.95.230.200:8081', '113.207.110.159:9000', '103.239.152.222', '58.20.133.137:9899', 'https://www.coologic.cn', 'https://47.101.56.126', '218.71.141.22:8088', '213.133.83.35', '61.181.143.170:9999', 'https://biuat.ibaiqiu.com', 'https://39.98.235.109', 'https://wiki.laolisafe.com', 'https://47.101.214.91', '118.25.145.105', '202.181.211.144:8081', '120.202.47.240:8000', 'https://120.55.23.61', '47.102.98.181:8080', 'liupanshui.witcp.com', '123.57.224.125', '47.111.114.17:82', '162.14.12.112:8002', 'nav.mhbdng.cn', 'https://horde.avic-digital.com', 'https://219.141.240.99', '117.27.235.72:9009', '218.29.42.138:7070', '106.125.252.82:8081', '220.174.235.18:11580', '122.224.77.115:8083', '120.27.226.131:8090', 'https://47.106.255.21', '117.25.175.221', '39.106.155.20', 'bi.genesismedtech.com', '60.28.76.137', '47.119.122.226', '39.101.132.202', '47.98.230.197', '223.244.238.121:7070', 'https://yulin.zbj.com', '120.199.26.182:8091', '115.238.36.43:8091', '59.50.108.178:8091', '218.75.2.218:83', 'https://shentuzhigang.blog.csdn.net', '113.102.205.138:8888', '103.20.251.85', '211.75.165.17:82', '101.132.237.50:6060', '111.39.109.64:7070', '113.162.55.253:8086', 'https://mms.opals.msad40.org', 'https://213.133.83.35', '47.97.197.193:8083', '182.92.6.224', '222.133.26.26:8095', '120.27.195.162', '223.99.192.12:8082', 'report.xmxc.com', '119.23.188.184', '156.236.117.116', '39.107.236.254:135', 'https://202.99.217.77', '118.190.38.254:8088', 'https://dev03-agro.dev.ms-test.net', '120.77.80.75:8080', 'www.scjc.top', '222.133.27.122:8095', 'https://www.beisoft.cn', 'https://hanzhong.zbj.com', 'https://bis-ind.narvi.opalsinfo.net', 'https://hbhs.sccs.opalsinfo.net', 'https://anu-gnec.kari.opalsinfo.net', 'https://mccs-ind.phoebe.opalsinfo.net', 'https://iobm.daphnis.opalsinfo.net', 'https://jac.cegep.opalsinfo.net', 'https://zhangjiajie.zbj.com', 'https://218.17.179.205:8443', 'https://langfang.zbj.com', 'https://zekai.zbj.com', 'https://help.zbj.com', 'https://zwork.zbj.com', '47.94.108.206', '114.55.69.225', 'www.e23dns.com', 'e23dns.com', '0523.job1001.com', '0903.job1001.com', '14.221.4.139:8888', '219.140.190.29', '182.92.110.67:8080', '116.128.206.12:8086', '58.211.153.238:8888', '14.221.4.49:8888', 'https://119.145.30.201:8088', '60.2.26.206:8089', 'bi.zjhuiren.com:81', 'bi.shyanzhen.cn', 'https://113.141.71.135', 'www.meijiamei.com:8086', 'https://techno.jma-webexhibition.com', 'https://testhelp.fanruan.com', 'https://cu.fanruan.com', '114.115.141.157', 'fr.kelti.cn:28080', 'https://8.133.164.110', '122.114.222.250:8000', '113.102.205.165:8888', '183.247.182.212:8081', '219.146.247.236:7005', '116.62.10.99:9080', 'mis.mainpokerv.net', '47.95.194.117:8091', '202.75.217.37:8080', '113.102.205.107:8888', 'bi.handeaxle.com:8075', '0530.job1001.com', 'fj.job1001.com', '114.86.205.9:8181', 'https://solution.zbj.com', 'gx.job1001.com', '0833.job1001.com', '0635.job1001.com', '0577.job1001.com', '0573.job1001.com', '58.210.32.210:8899', '113.102.207.184:8888', '110.86.9.187:8899', 'https://136.232.242.186', '221.5.11.93:18080', '60.21.217.66:8008', '180.208.32.38:8089', '113.102.207.175:8888', '36.153.225.118:1080', 'https://202.75.217.37:8443', '183.129.145.134:18080', '47.106.255.21', '47.104.192.2:82', '115.231.195.210:28080', '36.249.61.114:8083', '58.18.34.24', '103.38.41.22:82', '47.106.254.114', '8.133.164.110', '122.112.189.128', '58.42.234.196:81', '45.250.239.27', '218.71.141.22:8686', '220.248.50.18:8080', '139.186.193.79', '183.58.30.162:8080', 'www.gzbpm.com', '61.145.194.54', 'https://54.168.17.101', '47.111.114.33:82', '112.225.67.20:8088', 'www.cehmdfkvtu.cn', 'taxtsoft.com', '58.216.170.22:55555', '113.102.206.31:8888', 'bi.zyjkinfo.cn', '120.92.20.28', 'https://113.105.85.188', '222.185.161.228:9999', '111.230.210.168:8080', 'https://120.92.82.235', '59.56.253.42:8083', '111.17.186.113:8082', '47.111.114.91:82', '116.230.24.175:9100', '121.205.96.61', '1.180.195.24', '42.227.88.162:8088', '103.239.153.229:8081', 'https://report.yhglobal.cn', '59.63.163.252:8082', 'www.finereporthelp.com:8021', 'https://111.231.220.202', '221.228.203.3:6006', '59.63.163.252:8089', 'https://218.107.217.45:4430', 'https://54.223.225.199', 'https://42.48.108.118', '221.237.155.254:8181', '134.175.57.13:18080', 'https://39.107.110.83', '180.76.47.208:5051', 'fr.csgpower.com.cn:18080', 'https://152.136.213.171', '120.81.224.157:8085', 'qdm123.cn', 'www.qdm123.cn', '139.186.163.70', '8.136.107.124', '120.132.8.144', '118.190.38.254', '113.141.71.135', '39.107.110.83', 'dc.shuimuyc.com', 'tdr.cdhytd.com', 'rv1.cdhytd.com', 'fnp.cdhytd.com', 't5x.cdhytd.com', '2yw.cdhytd.com', '4aa.cdhytd.com', 'dh5.cdhytd.com', 'ssk.cdhytd.com', 'dpt.cdhytd.com', 'www.cdhytd.com', 'obpm_org.cdhytd.com', 'rxp.cdhytd.com', 'm8g.cdhytd.com', '7f5.cdhytd.com', 'ppv.cdhytd.com', '08a.cdhytd.com', '8mw.cdhytd.com', '2yq.cdhytd.com', 'f1f.cdhytd.com', 'pzf.cdhytd.com', 'fvh.cdhytd.com', '0ia.cdhytd.com', '08w.cdhytd.com', 'cicpa.wkinfo_com_cn.whhaihong.com', 'p1r.cdhytd.com', 'uyw.cdhytd.com', 'rvf.cdhytd.com', 'rl5.cdhytd.com', '222.cdhytd.com', 'rht.cdhytd.com', 'jt3.cdhytd.com', '2qu.cdhytd.com', 'l7h.cdhytd.com', 'www.teemlink_com.cdhytd.com', 'ljv.cdhytd.com', 'gse.cdhytd.com', 'rpn.cdhytd.com', '7jr.cdhytd.com', 'kgq.cdhytd.com', 'eso.cdhytd.com', 'www.51.la.cdhytd.com', '5pz.cdhytd.com', '9df.cdhytd.com', 'teemlink_com.cdhytd.com', '119.93.252.106:8088', '120.25.253.59:8080', 'https://52.80.249.177', '101.37.33.184:5000', '119.165.195.235:8088', '39.153.253.219', '59.45.19.210:3000', '106.52.108.145:8080', 'https://180.76.160.169', '119.254.225.126', '124.71.185.90:5000', '42.227.90.127:8088', '111.30.16.225:8083', '61.145.194.54:8081', '210.123.136.201', '139.224.239.143:8088', '218.63.75.16:8092', '42.227.91.60:8088', '115.183.25.22:8085', 'https://u14.com', 'https://www.wmdy.top', '123.56.87.78:8885', 'https://community.finereport.com', '220.182.49.154:8099', '124.71.185.90:4000', '42.227.89.6:8088', '116.227.237.155:9100', 'www.xmhehy.com', 'www.qhdlch.com', '119.84.139.156:81', '119.180.26.213:8888', '42.227.88.150:8088', '61.161.203.46:8080', '106.54.194.125:8081', '42.227.90.171:8088', 'https://www.xt12366.com', 'https://www.leyouwangluo.com', 'https://www.argentwing.com', '116.6.133.152:8080', '59.63.163.249:8082', '112.225.66.121:8088', '222.173.217.58:8888', 'https://cas.firstcare.com.cn', 'https://sso.firstcare.com.cn', '183.247.184.130:18080', 'dd.hnrr.com.cn', 'https://dd.jgyrzzl.com', 'https://106.54.194.125', 'fr.kc-cottrell.com', 'https://d.icolor.com.cn', '104.199.237.121', '59.63.163.251:8082', '119.254.225.126:8443', '222.65.253.27:8181', 'd.xinfangsheng.com', '39.65.111.67:8088', 'yqgl.hsln.cn:8080', 'https://report.multek.com', 'https://zb.huaxiacloud.com', 'www.sxinrj.com', '47.97.124.166:85', '42.227.88.12:8088', 'dss.zhibaizhi.com:8080', '123.57.213.208:8885', '60.31.249.44:9090', '42.237.156.100:8085', '110.7.24.45:9090', 'bi.zaopiaowang.com', '47.96.99.77', '110.7.24.64:9090', '110.7.24.12:9090', '110.7.24.60:9090', 'https://222.247.56.34', '124.89.89.230:8888', '154.204.161.178:8125', '111.229.116.144', '42.227.89.141:8088', 'report.techcode.com', '60.172.5.242:3389', 'https://www.jcbc.co.jp', '47.93.23.62', 'www.vns34566.com', 'www.88188shenbo.com', 'https://jackxiang.com', 'https://dj-littlesheep-bi.daojia.com.cn', 'https://210.202.34.168', '77.224.197.172:8000', 'however.98ds3088.cn', 'https://125.94.212.56', 'www.mil11.com', '106.54.194.125', 'https://60.248.112.9', '207.246.98.37:8080', 'zbj_com.kunminggangting.com', 'www.zbj_com.fuyuejz.com', 'https://163.177.24.7', '112.225.66.175:8088', 'www.trzpt.com', '42.247.25.102:8080', '118.126.103.87', 'https://180.167.181.204:8082', '222.76.27.49:9009', 'https://getappstoday.com', 'www.finereport.com.tw', 'finereport.com.tw', 'https://104.199.237.121', '122.226.4.254:8099', '220.182.49.142:8086', '111.132.5.164', 'https://vanillabrain.com', '116.230.31.6:9100', 'hr.hxytea.com:7778', 'abi.prosign.cn', '124.205.27.10:3002', '121.43.110.252:8082', 'www.eolefc.com', 'www.nsb62.com', 'www.oumrnf.com', '110.7.24.92:9090', '122.51.150.165', 'https://join.fanruan.com', 'https://dd.hnrr.com.cn', 'https://114.141.183.50', '140.249.24.206', 'bi.bjhr.com.cn', '125.64.9.71:8080', '115.198.55.80:18080', '47.105.139.244:9999', '47.102.212.62:9080', '116.230.30.19:9100', '47.93.23.62:8080', '60.209.18.206:8088', '115.28.154.155', '60.190.96.157:8080', '222.131.114.168:3002', '61.161.149.246:18080', 'https://59.41.223.234', '110.7.24.2:9090', '110.7.24.75:9090', '116.63.68.138:8083', 'mail.nnmh.net', 'nnmh.net', 'www.nnmh.net', '123.178.199.108:8081', 'zhinengpingtai.uuoid.com', '218.3.120.165', '47.105.153.153:8083', '117.25.177.138:7778', '116.227.233.65:9100', '14.104.85.74:8088', '113.108.243.202:82', '60.31.249.45:9090', '39.106.29.45:8090', '101.80.134.156:8181', '222.173.37.162:8182', '60.205.125.188:8080', '110.7.24.36:9090', '163.177.42.152', '111.231.92.193:8080', '116.230.30.81:9100', '120.55.59.200:8080', '120.25.253.59', '116.227.232.154:9100', 'https://cdn.hellobi.com', '110.7.24.43:9090', '110.7.24.25:9090', '140.249.24.206:8082', '110.7.24.49:9090', '119.122.114.172:2020'], [], []
    exploit = Exploit('zjhu.edu.cn', domainList, ipPortServiceList, webParamsList)
    exploit.run()