# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2022-08-06 11:08

from core.data import gLogger
from exploit.scripts.__template__ import Script
from core.component.asyncpool import PoolCollector

from exploit.service.ajp import ajp_scan
from exploit.service.dubbo import dubbo_scan
from exploit.service.ftp import ftp_scan
from exploit.service.jdwp import jdwp_scan
from exploit.service.ldap import ldap_scan
from exploit.service.log4j import log4j_scan
from exploit.service.memcache import memcache_scan
from exploit.service.mongodb import mongodb_scan
from exploit.service.mssql import mssql_scan
from exploit.service.mysql import mysql_scan
from exploit.service.postgresql import postgresql_scan
from exploit.service.proxy import proxy_scan
from exploit.service.redis import redis_scan
from exploit.service.rmi import rmi_scan
from exploit.service.rsync import rsync_scan
from exploit.service.smb import smb_scan
from exploit.service.weblogicT3 import weblogic_scan
from exploit.service.zookeeper import zookeeper_scan

import time
import asyncio
import traceback
import aiohttp


class EngineManager:
    def __init__(self, name):
        self.spend_time = 0
        self.source = 'PocScanner'
        self.name = name
        self._total_task_count = 0
        self._error_task_count = 0
        self._find_task_count = 0
        self.start_time = time.time()
        self.is_continue = True

        self.target_queue = None
        self.target_url_list = None
        self.target_module_list = None
        self.target_threads = None
        self.target_web_exploit_flag = None
        self.target_service_exploit_flag = None
        self.target_web_scan_func = None

        # print(self.module_list)

    def print_progress(self, manager: PoolCollector):
        found_count = self._find_task_count
        error_count = self._error_task_count
        remaining_count = manager.remain_task_count
        scanning_count = manager.scanning_task_count
        scanned_count = self._total_task_count - manager.remain_task_count
        total_count = self._total_task_count
        self.spend_time = time.time() - self.start_time
        print('%s found | %s error | %s remaining | %s scanning | %s scanned in %.2f seconds.(total %s)' % \
              (found_count, error_count, remaining_count, scanning_count, scanned_count, self.spend_time, total_count))

    async def _progress_daemon(self, manager: PoolCollector):
        while True:
            await asyncio.sleep(60)
            self.print_progress(manager)

    def set_target_queue(self, target_queue: asyncio.Queue):
        self.target_queue = target_queue

    def set_target_url_list(self, target_url_list: list):
        self.target_url_list = target_url_list

    def set_target_service_exploit_flag(self, target_service_exploit_flag):
        self.target_service_exploit_flag = target_service_exploit_flag

    def set_target_web_exploit_flag(self, target_web_exploit_flag):
        self.target_web_exploit_flag = target_web_exploit_flag

    def set_target_module_list(self, target_module_list: list):
        self.target_module_list = target_module_list

    def set_web_scan_func(self, target_web_scan_func):
        self.target_web_scan_func = target_web_scan_func

    def set_target_threads(self, target_threads):
        self.target_threads = target_threads

    # spend time about 5.23s
    async def _check_queue_is_empty(self):
        try:
            while True:
                if self.target_queue.empty():
                    self.is_continue = False
                    break
                else:
                    await asyncio.sleep(10)
        except Exception:
            pass

    async def _do_web_scan(self, script: Script, target, func_name='attack'):
        """
        @param script:
        @param target:
        @param func_name: default attack , or you can choose attack / detect / exec
        @return: void , if void is return none
        """
        vul_list = []
        target_addr = target['host']

        try:
            script_object = script(target_addr)
            # custom time to go
            # async with async_timeout.timeout(5):
            # set async timeout time
            if hasattr(script_object, func_name):
                if func_name == 'attack':
                    result = await script_object.attack()
                elif func_name == 'detect':
                    result = await script_object.detect()
                elif func_name == 'exec':
                    result = await script_object.exec()
                if isinstance(result, list):
                    vul_list.extend(result)
                elif isinstance(result, dict):
                    vul_list.append(result)
                # in scan_vul_submit_task, get a task from task_queue
                # if the task is
                # 加入的格式为如下图所示
                # [
                # {"seeyon": {"domain": [], "module": [module1(), module2(), module3()]}},
                # {"seeyon": {"domain": [], "module": [module1(), module2(), module3()]}}
                # ]
            else:
                gLogger.myscan_warn('please choose you func, which named -fn attack, -fn detect and -fn exec.')
        except AttributeError:
            gLogger.myscan_error('module func \'%s()\' not exist, please check \'%s\' script.' % (func_name, script.name))
            error_msg = traceback.format_exc()
            gLogger.myscan_error(error_msg)
            self._error_task_count += 1
        except (asyncio.TimeoutError, ConnectionResetError, ConnectionAbortedError):
            self._error_task_count += 1
        except (asyncio.CancelledError, ConnectionRefusedError, OSError):
            self._error_task_count += 1
        except (aiohttp.ServerConnectionError, aiohttp.http.HttpProcessingError, aiohttp.client.ClientError) as e:
            gLogger.myscan_error('target task id: %s error, the target is \'%s\', the error is %s' % (target['id'], target['host'], e.message))
            self._error_task_count += 1
        except Exception:
            error_msg = traceback.format_exc()
            gLogger.myscan_error('target task id: %s error, the target is \'%s\', the error is %s' % (target['id'], target['host'], error_msg))
            self._error_task_count += 1
        finally:
            try:
                if script_object and script_object.vul_list == [] and script_object.flag:
                    vul_list.append({'name': '{} FINGER'.format(script_object.name), 'url': script_object.target, 'software': script_object.name})
            except:
                pass
            self._find_task_count += 1
            return vul_list

    async def _do_service_scan(self, target):
        vul_list = []
        target_addr = target['host']
        target_service = target['service']
        try:
            if 'textui' in target_service:
                vul_list.append(await dubbo_scan(target_addr))
            elif 'ftp' in target_service:
                vul_list.append(await ftp_scan(target_addr))
            elif 'jdwp' in target_service:
                vul_list.append(await jdwp_scan(target_addr))
            elif '4560' in target_service:
                vul_list.append(await log4j_scan(target_addr))
            elif 'memcache' in target_service:
                vul_list.append(await memcache_scan(target_addr))
            elif 'mongodb' in target_service:
                vul_list.append(await mongodb_scan(target_addr))
            elif 'ms-sql-s' in target_service:  # mssql
                vul_list.append(await mssql_scan(target_addr))
            elif 'mysql' in target_service:
                vul_list.append(await mysql_scan(target_addr))
            elif 'postgresql' in target_service:
                vul_list.append(await postgresql_scan(target_addr))
            elif 'ldap' in target_service:
                vul_list.append(await ldap_scan(target_addr))
            elif 'redis' in target_service:
                vul_list.append(await redis_scan(target_addr))
            elif 'rmi' in target_service:
                vul_list.append(await rmi_scan(target_addr))
            elif 'microsoft-ds' in target_service:
                vul_list.append(await smb_scan(target_addr))  # smb
            elif 'rsync' in target_service:
                vul_list.append(await rsync_scan(target_addr))
            elif 'ssh' in target_service:
                vul_list.append(await smb_scan(target_addr))
            elif 'zookeeper' in target_service:
                vul_list.append(await zookeeper_scan(target_addr))
            elif 'socks' in target_service:
                vul_list.append(await proxy_scan(target_addr))
            elif 'afs3-callback' in target_service:
                vul_list.append(await weblogic_scan(target_addr))
            elif 'ajp13' in target_service:
                vul_list.append(await ajp_scan(target_addr))
        except (asyncio.TimeoutError, ConnectionResetError, ConnectionAbortedError):
            self._error_task_count += 1
        except (asyncio.CancelledError, ConnectionRefusedError, OSError):
            self._error_task_count += 1
        except (aiohttp.ServerConnectionError, aiohttp.http.HttpProcessingError, aiohttp.client.ClientError) as e:
            gLogger.myscan_error('target task id: %s error, the target is \'%s\', the error is %s' % (target['id'], target['host'], e.message))
            self._error_task_count += 1
        except Exception:
            error_msg = traceback.format_exc()
            gLogger.myscan_error('target task id: %s error, the target is \'%s\', the error is %s' % (target['id'], target['host'], error_msg))
            self._error_task_count += 1
        finally:
            self._find_task_count += 1
            return vul_list

    async def scan_vul_submit_task(self, manager):
        try:
            for target in self.target_url_list:
                if target['scan_type'] == 'web_scan':
                    if self.target_web_exploit_flag:
                        for module in self.target_module_list:
                            await manager.submit(self._do_web_scan, module, target, self.target_web_scan_func)
                elif target['scan_type'] == 'service_scan':
                    if self.target_service_exploit_flag:
                        await manager.submit(self._do_service_scan, target)
                self._total_task_count += 1
        except Exception as e:
            gLogger.myscan_error(e.args)
        finally:
            await manager.shutdown()

    async def _scan_vul_submit_task(self, manager):
        try:
            while True:
                if not self.target_queue.empty():
                    target = await self.target_queue.get()
                    if target['scan_type'] == 'web_scan':
                        # param -cs
                        # target_url_queue.put({'id': task_id, 'host': i, 'service': 'web', 'scan_type': 'web_scan'})
                        if self.target_web_exploit_flag:
                            for module in self.target_module_list:
                                await manager.submit(self._do_web_scan, module, target)
                    elif target['scan_type'] == 'service_scan':
                        # param -ss
                        # target_url_queue.put({'id': task_id, 'host': j, 'service': service, 'scan_type': 'service_scan'})
                        if self.target_service_exploit_flag:
                            await manager.submit(self._do_service_scan, target)
                    self._total_task_count += 1
                elif not self.is_continue:
                    break
                else:
                    await asyncio.sleep(0.1)
        except Exception as e:
            gLogger.myscan_error(e.args)
        finally:
            await manager.shutdown()

    async def scan_twice_vul_submit_task(self, manager):
        pass

    async def scan(self):
        """
        第一次scan_vul_submit_task is scan the same as some have

        @return:
        """
        # 根据线程数量创建一个PoolCollector（包含了一个异步池 + 一个异步队列）来进行管理
        async with PoolCollector.create(num_workers=self.target_threads) as manager:
            # 初始化检测队列函数，用于后面最终结束线程池使用
            # check some
            # asyncio.ensure_future(self._check_queue_is_empty())

            # 封装了一个打印进度条的函数，里面是一个死循环，用于每60s进行打印一次进度条的功能
            asyncio.ensure_future(self._progress_daemon(manager))

            # 提交运行的任务
            asyncio.ensure_future(self.scan_vul_submit_task(manager))

            # await asyncio.ensure_future(self.scan_twice_vul_submit_task(manager))
            # asyncio.ensure_future(self.scan_twice_vul_submit_task(manager))

            # 读取任务的结果
            async for record in manager.iter():
                if asyncio.isfuture(record):
                    # 判断是否是future对象，如果是的话那么就可以进行取结束完的结果
                    for record in record.result():
                        yield record
                else:
                    yield record

            # 结束之后，再次打印一次进度条
            self.print_progress(manager)
