# coding=utf-8

from Spider.BaiduSpider import *
from Spider.CtfrSpider import *
from Spider.NetSpider import *
from Spider.DnsBruteSpider import *
from Spider.DnsDataSpider import *
from Spider.PortSpider import *
from Spider.Common import resolve

from Exploit.AliveScan import *
from Exploit.IpUnauthExploit import *
from Exploit.HttpUnauthExploit import *
from Exploit.CmsExploit import *
from ThridLib.virustotal import *
from ThridLib.qianxun import *
from threading import Thread, Lock

import os
import argparse
import time
import sys
import asyncio
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

abs_path = os.getcwd() + os.path.sep


'''信息搜集类'''
class Spider(object):
    def __init__(self, domain):
        self.domain = domain  # 要爬取的域名
        self.thread_list = list()  # 线程启动列表
        self.task_list = list()  # 用来存储所有匹配到的域名
        self.clear_task_list = list()  # 存储整理过后的域名 [{"subdomain": "www.ncist.edu.cn","ip": "1.1.1.1","port":[7777,8888]}]
        self.lock = Lock()

    '''百度引擎关键词搜索的接口'''
    def baiduspider(self):
        baidu_list = BaiduSpider(self.domain).main()
        self.lock.acquire()
        self.task_list.extend(baidu_list)
        self.lock.release()

    '''HTTPS SSL证书子域名搜集'''
    def ctfrspider(self):
        ctfr_list = CrtrSpider(self.domain).main()
        self.lock.acquire()
        self.task_list.extend(ctfr_list)
        self.lock.release()

    '''FOFA/Shodan 信息搜集（域名 IP网段）'''
    def netspider(self):
        net_list = NetSpider(self.domain).main()
        self.lock.acquire()
        self.task_list.extend(net_list)
        self.lock.release()

    '''dns爆破查询子域名搜集'''
    # def dnsbrutespider(self):
    #     dnsbrute_list = subDomaindBrute(self.domain).main()
    #     self.lock.acquire()
    #     self.task_list.extend(dnsbrute_list)
    #     self.lock.release()

    '''dns数据库查询'''
    def dnsspider(self):
        dnsdatalist = DnsDataSpider(self.domain).main()
        self.lock.acquire()
        self.task_list.extend(dnsdatalist)
        self.lock.release()

    '''第三方JSON接口查询'''
    def thridspider(self):
        viruslist = VirusTotal(self.domain).main()
        self.lock.acquire()
        self.task_list.extend(viruslist)
        self.lock.release()

    '''第三方接口'''
    def qianxun(self):
        qianxunlist = Qianxun(self.domain).main()
        self.lock.acquire()
        self.task_list.extend(qianxunlist)
        self.lock.release()

    '''协程异步解析域名A'''
    def domainreservespider(self):
        logging.info("DomainReserve Start")
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        task = resolve.bulk_query_a(self.clear_task_list)  # 解析域名地址A记录
        self.clear_task_list = loop.run_until_complete(task)

        # 写文件，这里继续写
        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[2]
        index = 0
        while index < len(self.clear_task_list):
            # if self.clear_task_list[index]['subdomain'] != '':
            # 只写入子域名解析出来的ip
            if self.domain in self.clear_task_list[index]['subdomain']:
                web = list()
                web.append(self.clear_task_list[index]['subdomain'])
                web.append(self.clear_task_list[index]['ips'])
                worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(self.domain) + ".xlsx")
        workbook.close()

    '''ip反向域名解析'''
    def ipreserverspider(self):
        logging.info("IpReserverSpider Start")
        pass

    '''端口扫描 多进程异步执行，在洗数据result()之后 去获得该数组中的标识符为target为'yes'的字典对其中的ip进行扫描 然后write_file写入文件（这里是扫描子域名下的ip）'''
    def ipscanportspider(self):
        logging.info("PortScan Start")
        multiprocessing.freeze_support()
        temp_ips = []  # 用来记录扫描过的ip 防止多次扫描 节省时间
        pool = multiprocessing.Pool(5)
        for aaa in self.clear_task_list:
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
                        pool.apply_async(func=bbb.main)  # 异步运行,非阻塞
        pool.close()
        pool.join()

    '''这里进行清洗数据的操作'''
    def result(self):
        # 第一次 清理 去域名协议
        for i in self.task_list:
            if 'http' in i:
                self.task_list[self.task_list.index(i)] = i.split('//')[1]

        # 第二次 清理去重 去重复值
        self.task_list = list(set(self.task_list))

        # 第三次 可视化格式数据拼接
        # 拼接的格式如：[{"subdomain": "www.ncist.edu.cn","ips": "1.1.1.1","port":[7777,8888],"target","yes"}]
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
                info['ips'] = ''
                info['port'] = None
                info['target'] = 'subdomain'  # 作为子域名的一个标识符
                self.clear_task_list.append(info)

            # 第二种情况：非正常子域名 非正常ip 正常域名
            elif self.domain not in aa and not re.match(r'\d+.\d+.\d+:?\d?', aa):
                info['subdomain'] = aa
                info['ips'] = ''
                info['port'] = None
                info['target'] = 'webdomain'
                self.clear_task_list.append(info)

            # 第三种情况：非正常子域名 非正常域名 正常ip
            else:
                i = aa.split(':')
                if ':' in aa:
                    ip = i[0]
                    info['subdomain'] = ''
                    info['ips'] = ip
                    info['port'] = ip_port[ip]
                    info['target'] = 'ip'
                    self.clear_task_list.append(info)
                else:
                    ip = i[0]
                    info['ips'] = ip
                    info['port'] = list()
                    info['target'] = 'ip'
                    info['subdomain'] = ''
                    self.clear_task_list.append(info)

    '''程序的入口点'''
    def run(self):
        # self.thread_list.append(Thread(target=self.baiduspider,))
        # self.thread_list.append(Thread(target=self.ctfrspider,))
        self.thread_list.append(Thread(target=self.netspider,))
        # self.thread_list.append(Thread(target=self.dnsspider,))
        # self.thread_list.append(Thread(target=self.thridspider,))
        # self.thread_list.append(Thread(target=self.ipreserverspider,))
        # self.thread_list.append(Thread(target=self.qianxun))

        for i in self.thread_list:
            i.start()

        for i in self.thread_list:
            i.join()

        #  这里进行单一的查询，要不然直接导致网络通信不佳造成其他模块的无法使用
        # dnsbrute_list = subDomaindBrute(self.domain).main()
        # self.lock.acquire()
        # self.task_list.extend(dnsbrute_list)
        # self.lock.release()

        # 清洗整理数据
        self.result()

        # 异步解析A记录
        # self.domainreservespider()
        # print(self.clear_task_list)

        # 端口扫描，这里的端口扫描自己写的只扫子域名下的ip 可以自行更改target的字段
        # self.ipscanportspider()

        # 最后返回处理好的数据 交给Exploit类
        return self.clear_task_list


'''漏洞扫描类，自己全用多线程直接进行跑，难的也8会写'''
class Exploit(object):
    def __init__(self, domain, clear_task_list):
        self.thread_list = list()
        self.domain = domain
        self.clear_task_list = clear_task_list

    def AliveScan(self):
        AliveScan(self.domain, self.clear_task_list).main()

    def IpUnauthScan(self):
        IpUnauth(self.domain, self.clear_task_list).main()

    def HttpUnauthScan(self):
        HttpUnauth(self.domain, self.clear_task_list).main()

    def CmsScan(self):
        CmsScan(self.domain, self.clear_task_list).main()

    # SqlScan扫描 这个代码就不放了 主要是sqlmap配合python subprocess模块来对sqlmap显示的字符串进行判断是否存在注入
    def SqlScan(self):
        pass
        # SqlScan(self.domain, self.clear_task_list).main()

    def run(self):
        self.thread_list.append(Thread(target=self.AliveScan))
        self.thread_list.append(Thread(target=self.CmsScan))  # cms/框架扫描
        self.thread_list.append(Thread(target=self.IpUnauthScan))  # 未授权扫描ip
        self.thread_list.append(Thread(target=self.HttpUnauthScan))  # 未授权扫描http域名
        # self.thread_list.append(Thread(target=self.SqlScan)) # sql注入扫描

        for i in self.thread_list:
            i.start()

        for i in self.thread_list:
            i.join()


def parse_args():
    parser = argparse.ArgumentParser(prog='MyFrameWork',)
    parser.add_argument('-d', '--domain', type=str, required=True, help="Target domain.")
    parser.add_argument('-v', '--version', type=str, help='%(prog)s v1')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if not os.path.exists(abs_path + args.domain + ".xlsx"):
        Common_createXlxs(args.domain)
    starttime = time.time()
    spider = Spider(args.domain)
    clear_task_list = spider.run()
    # exploit = Exploit(args.domain, clear_task_list)
    # exploit.run()
    print("总共耗时时间为：" + str(time.time() - starttime))