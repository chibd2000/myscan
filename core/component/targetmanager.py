# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2022-08-06 11:08

from core.component.modulemanager import ModuleManager
from core.data import gLogger, path_dict
from core.component.enginemanager import EngineManager
from core.component.variablemanager import GlobalVariableManager
from core.utils.portwrapper import PortWrapper
from spider.clear import ClearSpider

from spider.third import ThirdSpider
from spider.beian import BeianSpider
from spider.baidu import BaiduSpider
from spider.bing import BingSpider
from spider.crt import CrtSpider
from spider.domain2ip import Domain2ipSpider
from spider.friendspider import FriendChainsSpider
from spider.githubspider import GithubSpider
from spider.netspace import NetSpider
from spider.ip2domain import Ip2domainSpider
from spider.port import PortScan
from spider.sslcerts import SSLSpider
from spider.alive import AliveSpider

from core.data import config_dict
from core.logger import CUSTOM_LOGGER_LEVEL

import openpyxl
import os
import asyncio
import sys


def ksubdomain(domain):
    gLogger.myscan_debug("ksubdomain_spider_start")
    ksub_domain_list = []
    ksubdomain_folder = './ksubdomain'
    ksubdomain_file = '{}/{}.txt'.format(ksubdomain_folder, domain)
    os.system('./ksubdomain/ksubdomain --skip-wild -d {} -o {}'.format(domain, ksubdomain_file))
    try:
        with open(ksubdomain_file, 'rt') as f:
            for each_line in f.readlines():
                each_line_split = each_line.split('=>')
                subdomain = each_line_split[0].strip()  # 子域名
                ksub_domain_list.append(subdomain)
        os.remove(ksubdomain_file)  # 删除临时文件
        gLogger.myscan_info('[{}] [{}] {}'.format('ksubdomain', len(ksub_domain_list), ksub_domain_list))
    except Exception as e:
        ksub_domain_list = []
    finally:
        return ksub_domain_list


class TargetManager:
    def __init__(self, task_name, target):
        self.task_name = task_name
        self.target_domain = None

        self.module_manager = ModuleManager()

        self.target_web_scan_func = 'attack'
        self.target_search_flag = False
        self.target_web_exploit_flag = False
        self.target_service_exploit_flag = False
        self.target_sql_exploit_flag = False

        self.target_show_module_flag = False
        self.target_find_module = None

        self.target_url = None
        self.target_fofa = None
        self.target_ips = None

        self.target_ip_file = None
        # self.target_domain_file = None
        self.target_url_file = None

        self.target_company = None
        self.target_ksub_domain = None
        self.target_threads = None
        self.target_module = None

        self.target_port = target.port

        self.domain_list = list()
        self.asn_list = list()
        self.ip_list = list()
        self.ip_port_list = list()
        self.ip_segment_list = list()
        self.domain_alive_list = list()

        self.ip_port_service_list = list()

        self._register_target_options(target)

    def write_file(self, web_lists, page):
        try:
            workbook = openpyxl.load_workbook(path_dict.ROOT_PATH + str(self.task_name) + ".xlsx")
            worksheet = workbook.worksheets[page]
            for web_info in web_lists:
                web = []
                for _ in web_info.values():
                    web.append(_)
                worksheet.append(web)
            workbook.save(path_dict.ROOT_PATH + str(self.task_name) + ".xlsx")
            workbook.close()
        except FileNotFoundError:
            gLogger.myscan_warn('if you want to record search and attack information, you need start with -o param.')
        except Exception as e:
            gLogger.myscan_warn('[{}] write_file error, error is {}'.format(self.target_domain, e.__str__()))

    @classmethod
    def create_target_manager(cls, task_name, parser):
        args = parser.parse_args()
        if not args.domain and not args.ip_file and not args.url_file \
                and not args.url and not args.ips and not args.fofa and not args.show and not args.find:
            parser.print_help(sys.stdout)
            exit(0)
        return cls(task_name, args)

    def _register_target_options(self, target):
        if target.debug:
            gLogger.set_level(CUSTOM_LOGGER_LEVEL.MYSCAN_DEBUG)

        if target.proxy:
            config_dict['proxy'] = target.proxy

        if target.ksub:
            self.target_ksub_domain = target.ksub

        if target.port:
            GlobalVariableManager.setValue('port_config', target.port)

        if target.threads:
            self.target_threads = target.threads

        if target.websearch:
            self.target_search_flag = True

        if target.servicescan:
            self.target_service_exploit_flag = True

        if target.webscan:
            self.target_web_exploit_flag = True

        if target.show:
            self.target_show_module_flag = True

        if target.find:
            self.target_find_module = target.find

        if target.webfunc:
            self.target_web_scan_func = target.webfunc

        if target.url:
            self.target_url = target.url

        if target.domain:
            self.target_domain = target.domain

        if target.fofa:
            self.target_fofa = target.fofa

        if target.ips:
            self.target_ips = target.ips

        if target.url_file:
            self.target_url_file = target.url_file

        # if target.domain_file:
        #     self.target_domain_file = target.domain_file

        if target.ip_file:
            self.target_ip_file = target.ip_file

        if target.module:
            self.target_module = target.module

        if target.company:
            self.target_company = target.company

    async def _domain_third_engine_api(self, target_domain):
        gLogger.myscan_debug("third_spider_start")
        result_list = await ThirdSpider(target_domain, self.task_name).main()
        self.domain_list.extend(result_list)

    async def _domain_search_engine_api(self, target_domain):
        gLogger.myscan_debug("beian_spider_start")
        gLogger.myscan_debug("bing_spider_start")
        gLogger.myscan_debug("baidu_spider_start")
        gLogger.myscan_debug("crt_spider_start")
        gLogger.myscan_debug("github_spider_start")
        task_list = [
            asyncio.create_task(BeianSpider(target_domain, self.task_name).main()),
            asyncio.create_task(CrtSpider(target_domain, self.task_name).main()),
            asyncio.create_task(BaiduSpider(target_domain, self.task_name).main()),
            asyncio.create_task(BingSpider(target_domain, self.task_name).main()),
            asyncio.create_task(GithubSpider(target_domain, self.task_name).main())
        ]
        result_list = await asyncio.gather(*task_list)
        for _ in result_list:
            if _ is not None:
                self.domain_list.extend(_)

    async def _domain_space_engine_api(self, target_domain):
        gLogger.myscan_debug("space_spider Start")
        result_list, self.asn_list, self.ip_list, self.ip_port_list = await NetSpider(target_domain, self.task_name).main()
        self.domain_list.extend(result_list)
        self.domain_list = list(set(self.domain_list))

    async def _friend_search_api(self, target_domain):
        gLogger.myscan_debug("friend_chains_spider_start")
        result_list = await FriendChainsSpider(target_domain, self.domain_list).main()
        self.domain_list.extend(result_list)
        self.domain_list = list(set(self.domain_list))

    async def _domain_2_ip_api(self, target_domain):
        gLogger.myscan_debug("domain_2_ip_spider_start")
        result_list = await Domain2ipSpider(target_domain, self.task_name, self.domain_list).main()
        for _ in result_list:
            self.ip_list.append(_['ip'])
        self.ip_list = list(set(self.ip_list))

    async def _ip_2_domain_api(self, target_domain):
        gLogger.myscan_debug("ip_2_domain_spider_start")
        self.ip_list = [i for i in self.ip_list if i]
        result_list = await Ip2domainSpider(target_domain, self.task_name, self.ip_list).main()
        self.domain_list.extend(result_list)
        self.domain_list = list(set(self.domain_list))

    async def _ssl_search_api(self, target_domain):
        gLogger.myscan_debug("_ssl_search_spider_start")
        result_list = await SSLSpider(target_domain, self.task_name, self.domain_list).main()
        self.domain_list.extend(result_list)
        self.domain_list = list(set(self.domain_list))

    async def _port_scan_api(self, target_domain):
        gLogger.myscan_debug("_port_scan_spider_start")
        port_config = GlobalVariableManager.getValue('port_config')
        for i in self.ip_list:
            flag = True
            for j in self.ip_port_list:
                if i == j['ip']:
                    flag = False
                    break
            if flag:
                self.ip_port_list.append({'ip': i, 'port': []})
        PortWrapper.generate_port(port_config, self.ip_port_list)
        self.ip_port_service_list, http_protocol_list = await PortScan(target_domain, self.task_name, self.ip_port_list).main()
        self.domain_list.extend(http_protocol_list)

    async def _alive_search_api(self, target_domain):
        gLogger.myscan_debug("_alive_search_spider_start")
        self.domain_alive_list = await AliveSpider(target_domain, self.task_name, self.domain_list).main()

    async def _search_func(self, target_domain):
        if self.target_ksub_domain:
            self.domain_list.extend(ksubdomain(target_domain))
        await self._domain_third_engine_api(target_domain)
        await self._domain_search_engine_api(target_domain)
        await self._domain_space_engine_api(target_domain)
        await self._friend_search_api(target_domain)
        await self._domain_2_ip_api(target_domain)
        await self._ip_2_domain_api(target_domain)
        await self._ssl_search_api(target_domain)

        ClearSpider(target_domain, self.task_name).flush_asn(self.asn_list)
        ClearSpider(target_domain, self.task_name).flush_ip_segment(self.ip_list, self.ip_segment_list)

        self.domain_list = list(set(self.domain_list))
        await self._port_scan_api(target_domain)
        await self._alive_search_api(target_domain)

    def free_memory(self):
        self.domain_list[:], self.asn_list[:], self.ip_list[:], self.ip_port_list[:] = [], [], [], []
        self.ip_segment_list[:], self.domain_alive_list[:], self.ip_port_service_list[:] = [], [], []

    async def search(self):
        flag = True

        if self.target_show_module_flag and flag:
            self.module_manager.show_module()
            flag = False
            exit(0)

        if self.target_find_module and flag:
            self.module_manager.find_module(self.target_find_module)
            flag = False
            exit(0)

        # python3 batch.py -d test.com -ws -> ok
        # python3 batch.py -d test.com -ws -cs -> ok
        # python3 batch.py -d test.com -ws -cs -ss -> ok
        if self.target_domain and flag:
            if self.target_search_flag:
                await self._search_func(self.target_domain)
            flag = False

        # python3 batch.py -c 横戈安全有限公司 -> no
        if self.target_company and flag:
            flag = False

        # python3 batch.py -fs "title=\"系统管理\"" -cs  -> ok
        # python3 batch.py -fs "title=\"系统管理\"" -m exploit.a.b -cs -> ok
        # python3 batch.py -fs "title=\"系统管理\"" -m exploit.a.b,exploit.c.d -cs -> ok

        if self.target_fofa and flag:
            from core.netapi import fofaSearch
            self.domain_alive_list.extend(await fofaSearch(self.target_fofa))
            flag = False

        # python3 batch.py -u test.com -cs  -> ok
        # python3 batch.py -u test.com -m exploit.a.b -cs  -> ok
        # python3 batch.py -u test.com -m exploit.a.b, exploit.c.d -cs  -> ok

        if self.target_url and flag:
            self.domain_alive_list.append(self.target_url)
            flag = False

        # python3 batch.py -i 127.0.0.1 -> ok
        # python3 batch.py -i 127.0.0.1 -p 9001 -> ok
        # python3 batch.py -i 127.0.0.1 -p 9001,9002,9003 -> ok
        # python3 batch.py -i 127.0.0.1 -p 9001-9005 -> ok

        # python3 batch.py -i 127.0.0.1 -cs
        # python3 batch.py -i 127.0.0.1 -m exploit.a.b -cs
        # python3 batch.py -i 127.0.0.1 -m exploit.a.b,exploit.c.d -cs
        # python3 batch.py -i 127.0.0.1 -m exploit.a.b -cs -ss
        # python3 batch.py -i 127.0.0.1 -m exploit.a.b,exploit.c.d -cs -ss

        # python3 batch.py -i 127.0.0.1 -p 9001 -m exploit.a.b -cs
        # python3 batch.py -i 127.0.0.1 -p 9001 -m exploit.a.b,exploit.c.d -cs
        # python3 batch.py -i 127.0.0.1 -p 9001 -m exploit.a.b -cs -ss
        # python3 batch.py -i 127.0.0.1 -p 9001 -m exploit.a.b,exploit.c.d -cs -ss

        # python3 batch.py -i 127.0.0.1 -p 9001,9002,9003 -m exploit.a.b -cs
        # python3 batch.py -i 127.0.0.1 -p 9001,9002,9003 -m exploit.a.b,exploit.c.d -cs
        # python3 batch.py -i 127.0.0.1 -p 9001,9002,9003 -m exploit.a.b -cs -ss
        # python3 batch.py -i 127.0.0.1 -p 9001,9002,9003 -m exploit.a.b,exploit.c.d -cs -ss

        # python3 batch.py -i 127.0.0.1 -p 9001-9005 -m exploit.a.b -cs
        # python3 batch.py -i 127.0.0.1 -p 9001-9005 -m exploit.a.b,exploit.c.d -cs
        # python3 batch.py -i 127.0.0.1 -p 9001-9005 -m exploit.a.b -cs -ss
        # python3 batch.py -i 127.0.0.1 -p 9001-9005 -m exploit.a.b,exploit.c.d -cs -ss

        if self.target_ips and flag:
            self.ip_port_list = PortWrapper.generate_format(self.target_ips)
            port_config = GlobalVariableManager.getValue('port_config')
            PortWrapper.generate_port(port_config, self.ip_port_list)
            self.ip_port_service_list, http_protocol_list = await PortScan(self.target_domain, self.task_name, self.ip_port_list).main()
            self.domain_alive_list.extend(http_protocol_list)

        # python3 batch.py -uf url.txt -ws
        # python3 batch.py -uf url.txt -ws -cs
        # python3 batch.py -uf url.txt -ws -m exploit.a.b -cs
        # python3 batch.py -uf url.txt -ws -m exploit.a.b,exploit.c.d -cs
        # python3 batch.py -uf url.txt -ws -cs -ss
        # python3 batch.py -uf url.txt -ws -m exploit.a.b -cs -ss
        # python3 batch.py -uf url.txt -ws -m exploit.a.b,exploit.c.d -cs -ss
        if self.target_url_file and flag:
            self.domain_alive_list = [domain.strip('\n') for domain in open(self.target_url_file, 'r').readlines()]


        # python3 batch.py -df domain.txt -ws
        # python3 batch.py -df domain.txt -ws -cs
        # python3 batch.py -df domain.txt -ws -m exploit.a.b -cs
        # python3 batch.py -df domain.txt -ws -m exploit.a.b,exploit.c.d -cs
        # python3 batch.py -df domain.txt -ws -cs -ss
        # python3 batch.py -df domain.txt -ws -m exploit.a.b -cs -ss
        # python3 batch.py -df domain.txt -ws -m exploit.a.b,exploit.c.d -cs -ss
        # if self.target_domain_file and flag:
        #     self.domain_list = [domain.strip('\n') for domain in open(self.target_domain_file, 'r').readlines()]
        #     for domain in self.domain_list:
        #         if self.target_search_flag:
        #             await self._search_func(domain)

        # python3 batch.py -if ip.txt -cs
        # python3 batch.py -if ip.txt -m exploit.a.b -cs
        # python3 batch.py -if ip.txt -m exploit.a.b,exploit.c.d -cs
        # python3 batch.py -if ip.txt -cs -ss
        # python3 batch.py -if ip.txt -m exploit.a.b -cs -ss
        # python3 batch.py -if ip.txt -m exploit.a.b,exploit.c.d -cs -ss
        if self.target_ip_file and flag:
            self.ip_list = [scan_ip.strip('\n') for scan_ip in open(self.target_ip_file, 'r').readlines()]
            self.ip_port_list = PortWrapper.generate_format(self.ip_list)
            port_config = GlobalVariableManager.getValue('port_config')
            PortWrapper.generate_port(port_config, self.ip_port_list)
            self.ip_port_service_list, http_protocol_list = await PortScan(self.target_domain, self.task_name, self.ip_port_list).main()
            self.domain_alive_list.extend(http_protocol_list)

    async def _register_target(self):

        target_url_queue = asyncio.Queue(-1)
        task_id = 1

        # web类型
        for i in self.domain_alive_list:
        # for i in ['https://jhlxj.net']:
            await target_url_queue.put({'id': task_id, 'host': i[:-1] if i.endswith('/') else i, 'service': 'web', 'scan_type': 'web_scan'})
            task_id += 1

        # service类型
        for i in self.ip_port_service_list:
            service = i['service']
            for j in i['ip']:
                await target_url_queue.put({'id': task_id, 'host': j, 'service': service, 'scan_type': 'service_scan'})
                task_id += 1

        return target_url_queue

    def _register_target_list(self):

        target_url_list = list()
        task_id = 1

        # web类型
        for i in self.domain_alive_list:
        # for i in ['https://jhlxj.net']:
            target_url_list.append({'id': task_id, 'host': i[:-1] if i.endswith('/') else i, 'service': 'web', 'scan_type': 'web_scan'})
            task_id += 1

        # service类型
        for i in self.ip_port_service_list:
            service = i['service']
            for j in i['ip']:
                target_url_list.append({'id': task_id, 'host': j, 'service': service, 'scan_type': 'service_scan'})
                task_id += 1

        return target_url_list

    async def scan(self, loop=None):
        engine_manager = EngineManager(self.task_name)

        # async_queue = await self._register_target()
        # self.engine_manager.set_target_queue(async_queue)

        if engine_manager.target_url_list is None:
            target_url_list = self._register_target_list()
            engine_manager.set_target_url_list(target_url_list)

        if engine_manager.target_web_exploit_flag is None:
            engine_manager.set_target_web_exploit_flag(self.target_web_exploit_flag)

        if engine_manager.target_service_exploit_flag is None:
            engine_manager.set_target_service_exploit_flag(self.target_service_exploit_flag)

        if engine_manager.target_module_list is None:
            self.module_manager.load_module('exploit', self.target_module)
            engine_manager.set_target_module_list(self.module_manager.get_load_module_list())

        if engine_manager.target_threads is None:
            engine_manager.set_target_threads(self.target_threads)

        if engine_manager.target_web_scan_func is None:
            engine_manager.set_web_scan_func(self.target_web_scan_func)

        result_list = []
        async for result in engine_manager.scan():
            if result:
                result_list.append(result)

        gLogger.myscan_info(result_list)
        self.write_file(result_list, 14)

