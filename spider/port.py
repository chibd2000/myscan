# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-02 13:18

from core.public import *
from core.data import gLogger
from core.setting import REGEXP_TITLE_STRING
from spider import BaseSpider
from spider.common.banner import ALLPROBES, ALL_GUESS_SERVICE
from async_timeout import timeout
from ipaddress import ip_address
import zlib
import ssl
import codecs
import asyncio


def compile_pattern(allprobes):
    """编译re的正则表达式"""
    for probe in allprobes:
        matches = probe.get('matches')
        if isinstance(matches, list):
            for match in matches:
                try:
                    # pattern, _ = codecs.escape_decode(match.get('pattern'))
                    pattern = match.get('pattern').encode('utf-8')
                    match['pattern_compiled'] = re.compile(pattern, re.IGNORECASE | re.DOTALL)
                except Exception as err:
                    match['pattern_compiled'] = ''
        softmatches = probe.get('softmatches')
        if isinstance(softmatches, list):
            for match in softmatches:
                try:
                    match['pattern_compiled'] = re.compile(match.get('pattern'), re.IGNORECASE | re.DOTALL)
                except Exception as err:
                    match['pattern_compiled'] = ''
    return allprobes


def get_ssl_context():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.load_verify_locations('pymotw.crt')
    return ssl_context


class ScanEngine:
    async def send_tcp_request(self, host, port, payload, size=1024, ssl_context=None):
        """Send tcp payloads by port number."""
        try:
            with timeout(1.25):
                reader, writer = await asyncio.open_connection(host, port, ssl=ssl_context)
                writer.write(payload)
                await writer.drain()
                data = await reader.read(size)
                writer.close()
            return data
        except ConnectionError:
            raise ConnectionError from None
        except Exception:
            return None

    async def send_probestring_request(self, host, port, protocol, probe):
        """根据nmap的probestring发送请求数据包"""
        proto = probe['probe']['protocol']
        payload = probe['probe']['probestring']
        payload, _ = codecs.escape_decode(payload)
        response = ''
        if proto.upper() == protocol.upper():
            if protocol.upper() == 'TCP':
                response = await self.send_tcp_request(host, port, payload)
        return response


class CustomServiceInfo(ScanEngine):
    def __init__(self):
        self.name = ''
        self.probe = ''

    def send_custom_probe_request(self):
        pass


class JdwpServicePlugin(CustomServiceInfo):
    def __init__(self):
        super().__init__()
        self.name = 'jdwp_service_scan_plugin'
        self.probe = b'JDWP-Handshake'
        self.service = 'jdwp'


CUSTOM_SERVICE_PLUGIN_LIST = [JdwpServicePlugin()]


class ServiceScanEngine(ScanEngine):

    def __init__(self):
        self.name = 'service_scan_engine'
        self.custom_service_plugin_list = [JdwpServicePlugin()]
        self.all_probes = compile_pattern(json.loads(zlib.decompress(base64.b64decode(ALLPROBES))))
        self.all_guess_services = json.loads(zlib.decompress(base64.b64decode(ALL_GUESS_SERVICE)))
        self.ssl_context = get_ssl_context()
        self.finish_task_num = 0
        self.error_task_num = 0
        self.remain_task_num = 0

    @property
    def get_finish_task_num(self):
        return self.finish_task_num

    @property
    def get_error_task_num(self):
        return self.error_task_num

    # 快扫模式（采用）
    async def quick_scan(self, host, port, protocol):
        try:

            in_probes, ex_probes = self.filter_probes_by_port(port, self.all_probes)
            probes = self.sort_probes_by_rarity(in_probes)

            # 如果第一次不是http，那么就代表着除http以外的服务，那么再根据相应指定端口对应的probe来进行匹配
            for probe in probes:
                response = await self.send_probestring_request(host, port, protocol, probe)
                if response is not None:
                    record = await self.get_port_service_information(host, port, response, probe)
                    if record is not None:
                        self.finish_task_num += 1
                        return record

            # 优先查询自定义的脚本特征
            for plugin in self.custom_service_plugin_list:
                custom_response = await plugin.send_tcp_request(host, port, plugin.probe)
                if custom_response is not None:
                    nmap_service, nmap_fingerprint = self.match_probe_pattern(custom_response, plugin.probe)
                    if bool(nmap_fingerprint):
                        record = {'ip': str(host), 'port': str(port), 'service': str(nmap_service), 'title': '','versioninfo': str(nmap_fingerprint)}
                        self.finish_task_num += 1
                        gLogger.myscan_info('scan host: %s:%s service: %s' % (str(host), str(port), str(nmap_service)))
                        return record

            # 如果指定端口对应的probe都无法匹配，那么该端口就不是默认端口，所以这里的话就是发送其他端口的probe来进行匹配
            scan_count = 0
            for probe in ex_probes:
                response = await self.send_probestring_request(host, port, protocol, probe)
                if response is not None:
                    record = await self.get_port_service_information(host, port, response, probe)
                    if record is not None:
                        self.finish_task_num += 1
                        return record

                # 这个20的数量，自己来调配，个人认为20是比较合适的
                scan_count += 1
                if scan_count > 20:
                    self.finish_task_num += 1
                    return None
        except ConnectionError:
            self.error_task_num += 1
        except Exception:
            self.error_task_num += 1
            pass

    # 慢扫模式（弃用）
    # async def slow_scan_bypass_cdn(self, host, port_list, protocol):
    #     port_service_task_list = []
    #     alive_port_count = 0
    #     scan_count = 0
    #     for port in port_list:
    #         # print('[+] scan %s:%s' % (host, port))
    #         in_probes, ex_probes = self.filter_probes_by_port(port, self.all_probes)
    #         probes = self.sort_probes_by_rarity(in_probes)
    #         finger_flag = False
    #         if alive_port_count > 25:
    #             gLogger.myscan_warn('scan host: %s is cdn, so skip it' % str(host))
    #             self.error_task_num += 1
    #             return None
    #         try:
    #             # 优化扫描速度，如果为内网地址的话就会浪费很多时间
    #             try:
    #                 if ip_address(host) and ip_address(host).is_private:
    #                     gLogger.myscan_warn('scan host: %s is private, so skip it' % str(host))
    #                     self.error_task_num += 1
    #                     return None
    #             except:
    #                 pass
    #
    #             # 优先查询自定义的脚本特征
    #             for plugin in self.custom_service_plugin_list:
    #                 custom_response = await plugin.send_tcp_request(host, port, plugin.probe)
    #                 if custom_response is None:
    #                     break
    #                 nmap_service, nmap_fingerprint = self.match_probe_pattern(custom_response, plugin.probe)
    #                 if bool(nmap_fingerprint):
    #                     record = {'ip': str(host), 'port': str(port), 'service': str(nmap_service), 'title': '', 'versioninfo': str(nmap_fingerprint)}
    #                     # print('scan host: %s:%s service: %s' % (host, port, nmap_service))
    #                     gLogger.myscan_info('scan host: %s:%s service: %s' % (str(host), str(port), str(nmap_service)))
    #                     port_service_task_list.append(record)
    #                     finger_flag = True
    #                     break
    #             if finger_flag:
    #                 continue
    #
    #             # 如果第一次不是http，那么就代表着除http以外的服务，那么再根据相应指定端口对应的probe来进行匹配
    #             for probe in probes:
    #                 response = await self.send_probestring_request(host, port, protocol, probe)
    #                 if response is not None:
    #                     record = await self.get_port_service_information(host, port, response, probe)
    #                     if record is not None:
    #                         port_service_task_list.append(record)
    #                         alive_port_count += 1
    #                         finger_flag = True
    #                         break
    #                 scan_count += 1
    #             if finger_flag:
    #                 continue
    #             scan_count = 0
    #
    #             # 如果指定端口对应的probe都无法匹配，那么该端口就不是默认端口，所以这里的话就是发送其他端口的probe来进行匹配
    #             for probe in ex_probes:
    #                 response = await self.send_probestring_request(host, port, protocol, probe)
    #                 if response is not None:
    #                     record = await self.get_port_service_information(host, port, response, probe)
    #                     if record is not None:
    #                         port_service_task_list.append(record)
    #                         alive_port_count += 1
    #                         finger_flag = True
    #                         break
    #                 scan_count += 1
    #                 # 这个20的数量，自己来调配，个人认为20是比较合适的
    #                 if scan_count > 20:
    #                     break
    #             if finger_flag:
    #                 continue
    #         # except TimeoutError:
    #         #     pass
    #         except Exception:
    #             pass
    #     self.finish_task_num += 1
    #     return port_service_task_list

    async def get_port_service_information(self, host, port, response, probe):
        nmap_service, nmap_fingerprint = self.match_probe_pattern(response, probe)
        http_ssl_probe = bytes('GET / HTTP/1.0\r\n\r\n', 'utf-8')
        if b'HTTP' in response:
            http_content = await self.send_tcp_request(host, port, http_ssl_probe, -1)
            http_title = self.get_http_service_title(http_content)
            if b'400 Bad Request' in http_content:
                http_ssl_content = await self.send_tcp_request(host, port, http_ssl_probe, -1, ssl_context=self.ssl_context)
                ssl_title = self.get_http_service_title(http_ssl_content)
                record = {'ip': str(host), 'port': str(port), 'service': 'http/ssl', 'title': str(http_ssl_content), 'versioninfo': str(nmap_fingerprint)}
                # print('scan host: %s:%s port_service: %s title: %s' % (host, port, 'http/ssl', ssl_title))
                gLogger.myscan_info('scan host: %s:%s service: %s title: %s' % (host, port, 'http/ssl', ssl_title))
            else:
                record = {'ip': str(host), 'port': str(port), 'service': 'http', 'title': str(http_title), 'versioninfo': str(nmap_fingerprint)}
                # print('scan host: %s:%s port_service: %s title: %s' % (host, port, 'http', http_title))
                gLogger.myscan_info('scan host: %s:%s service: %s title: %s' % (host, port, 'http', http_title))
            return record
        elif 'ssl' == nmap_service:
            http_ssl_content = await self.send_tcp_request(host, port, http_ssl_probe, -1, ssl_context=self.ssl_context)
            http_title = self.get_http_service_title(http_ssl_content)
            record = {'ip': str(host), 'port': str(port), 'service': 'http/ssl', 'title': http_title, 'versioninfo': str(nmap_fingerprint)}
            # print('scan host: %s:%s port_service: %s title: %s' % (host, port, 'http/ssl', http_title))
            gLogger.myscan_info('scan host: %s:%s service: %s title: %s' % (host, port, 'http/ssl', http_title))
            return record
        else:
            if bool(nmap_fingerprint):
                record = {'ip': str(host), 'port': str(port), 'service': str(nmap_service), 'title': '', 'versioninfo': str(nmap_fingerprint)}
                # print('scan host: %s:%s port_service: %s' % (host, port, nmap_service))
                gLogger.myscan_info('scan host: %s:%s service: %s' % (host, port, nmap_service))
                return record
        return None

    def match_probe_pattern(self, data, probe):
        """Match tcp/udp response based on nmap probe pattern."""
        nmap_service, nmap_fingerprint = "", {}
        if not data:
            return nmap_service, nmap_fingerprint
        try:
            matches = probe['matches']
            for match in matches:
                pattern_compiled = match['pattern_compiled']
                rfind = pattern_compiled.findall(data)
                if rfind and ("versioninfo" in match):
                    nmap_service = match['service']
                    versioninfo = match['versioninfo']
                    rfind = rfind[0]
                    if isinstance(rfind, str) or isinstance(rfind, bytes):
                        rfind = [rfind]
                    if re.search('\$P\(\d\)', versioninfo) is not None:
                        for index, value in enumerate(rfind):
                            dollar_name = "$P({})".format(index + 1)
                            versioninfo = versioninfo.replace(dollar_name, value.decode('utf-8', 'ignore'))
                    elif re.search('\$\d', versioninfo) is not None:
                        for index, value in enumerate(rfind):
                            dollar_name = "${}".format(index + 1)
                            versioninfo = versioninfo.replace(dollar_name, value.decode('utf-8', 'ignore'))
                    nmap_fingerprint = self.match_version_info(versioninfo)
                    if nmap_fingerprint is None:
                        continue
                    else:
                        return nmap_service, nmap_fingerprint
        except Exception as e:
            return nmap_service, nmap_fingerprint
        try:
            matches = probe['softmatches']
            for match in matches:
                # pattern = match['pattern']
                pattern_compiled = match['pattern_compiled']

                # https://github.com/nmap/nmap/blob/master/service_scan.cc#L476
                # regex = re.compile(pattern, re.IGNORECASE | re.DOTALL)

                rfind = pattern_compiled.findall(data)

                if rfind and ("versioninfo" in match):
                    nmap_service = match['service']
                    return nmap_service, nmap_fingerprint
        except Exception as e:
            return nmap_service, nmap_fingerprint
        return nmap_service, nmap_fingerprint

    def match_version_info(self, versioninfo):
        """Match Nmap versioninfo"""

        record = {"vendorproductname": [],"version": [],"info": [],"hostname": [],"operatingsystem": [],"cpename": []}

        if "p/" in versioninfo:
            regex = re.compile(r"p/([^/]*)/")
            vendorproductname = regex.findall(versioninfo)
            record["vendorproductname"] = vendorproductname

        if "v/" in versioninfo:
            regex = re.compile(r"v/([^/]*)/")
            version = regex.findall(versioninfo)
            record["version"] = version

        if "i/" in versioninfo:
            regex = re.compile(r"i/([^/]*)/")
            info = regex.findall(versioninfo)
            record["info"] = info

        if "h/" in versioninfo:
            regex = re.compile(r"h/([^/]*)/")
            hostname = regex.findall(versioninfo)
            record["hostname"] = hostname

        if "o/" in versioninfo:
            regex = re.compile(r"o/([^/]*)/")
            operatingsystem = regex.findall(versioninfo)
            record["operatingsystem"] = operatingsystem

        if "d/" in versioninfo:
            regex = re.compile(r"d/([^/]*)/")
            devicetype = regex.findall(versioninfo)
            record["devicetype"] = devicetype

        if "cpe:/" in versioninfo:
            regex = re.compile(r"cpe:/a:([^/]*)/")
            cpename = regex.findall(versioninfo)
            record["cpename"] = cpename
        if record == {"vendorproductname": [], "version": [], "info": [], "hostname": [], "operatingsystem": [], "cpename": []}:
            return None
        return record

    def sort_probes_by_rarity(self, probes):
        """Sorts by rarity
        """
        new_list = sorted(probes, key=lambda k: k['rarity']['rarity'])
        return new_list

    def filter_probes_by_port(self, port, probes):
        """通过端口号进行过滤,返回强符合的probes和弱符合的probes"""
        included = []
        excluded = []
        for probe in probes:
            if "ports" in probe:
                ports = probe['ports']['ports']
                if self.is_port_in_range(port, ports):
                    included.append(probe)
                else:  # exclude ports
                    excluded.append(probe)
            elif "sslports" in probe:
                sslports = probe['sslports']['sslports']
                if self.is_port_in_range(port, sslports):
                    included.append(probe)
                else:  # exclude sslports
                    excluded.append(probe)
            else:  # no [ports, sslports] settings
                excluded.append(probe)
        return included, excluded

    def is_port_in_range(self, port, nmap_port_rule):
        """Check port if is in nmap port range"""
        bret = False

        ports = nmap_port_rule.split(',')  # split into serval string parts
        if str(port) in ports:
            bret = True
        else:
            for nmap_port in ports:
                if "-" in nmap_port:
                    s, e = nmap_port.split('-')
                    if int(port) in range(int(s), int(e)):
                        bret = True
        return bret

    def get_http_service_title(self, content):
        title = ''
        text = ''
        try:
            detect_encode = chardet.detect(content)  # 利用chardet模块检测编码
            text = content.decode(detect_encode['encoding'])
            title = re.findall(REGEXP_TITLE_STRING, text, re.S | re.I)[0]
        except Exception:
            try:
                title = text[:15].strip('\r\n').strip('\n')
                if title == '':
                    title = '获取失败'
            except:
                title = '获取失败'
        finally:
            return title


class PortScan(BaseSpider):
    def __init__(self, domain, name, ip_port_list):
        super().__init__()
        self.domain = domain
        self.name = name
        self.source = 'PortSpider'
        self.ip_port_list = ip_port_list
        self.service_scan_engine = ServiceScanEngine()
        self.ip_port_service_list = []
        self.http_ssl_protocol_list = []
        self.all_task_num = 0
        self.start_time = time.time()
        self.spent_time = 0

    # 快扫模式（采用）
    async def quick_scan(self, semaphore, ip, port):
        async with semaphore:
            result = await self.service_scan_engine.quick_scan(ip, port, 'tcp')
            if result is not None:
                self.res_list.append({'ip': str(result.get('ip')), 'port': str(result.get('port')), 'service': str(result.get('service')), 'title': str(result.get('title')), 'versioninfo': str(result.get('versioninfo'))})
                flag = True
                for ip_port_service in self.ip_port_service_list:
                    if ip_port_service:
                        service = ip_port_service.get('service')
                        if service == result.get('service'):
                            flag = False
                            ip_port_service['ip'].append('{}:{}'.format(result['ip'], result['port']))
                if flag:
                    self.ip_port_service_list.append({'service': str(result.get('service')), 'ip': ['{}:{}'.format(result['ip'], result['port'])]})

    # 慢速扫描模式（弃用）
    # async def slow_scan_bypass_cdn(self, semaphore, ip, port):
    #     async with semaphore:
    #         result_list = await self.service_scan_engine.slow_scan_bypass_cdn(ip, port, 'tcp')
    #         if result_list is not None:
    #             for result in result_list:
    #                 self.res_list.append({'ip': str(result.get('ip')), 'port': str(result.get('port')), 'service': str(result.get('service')), 'title': str(result.get('title')), 'versioninfo': str(result.get('versioninfo'))})
    #                 flag = True
    #                 for ip_port_service in self.ip_port_service_list:
    #                     if ip_port_service:
    #                         service = ip_port_service.get('service')
    #                         if service == result.get('service'):
    #                             flag = False
    #                             ip_port_service['ip'].append('{}:{}'.format(result['ip'], result['port']))
    #                 if flag:
    #                     self.ip_port_service_list.append({'service': str(result.get('service')), 'ip': ['{}:{}'.format(result['ip'], result['port'])]})

    def print_progross(self):
        self.spend_time = time.time() - self.start_time
        print('%s found | %s error | %s remaining | %s scanned in %.2f seconds.(total %s)' % \
              (self.service_scan_engine.finish_task_num,
               self.service_scan_engine.error_task_num,
               self.all_task_num - self.service_scan_engine.finish_task_num - self.service_scan_engine.error_task_num,
               self.service_scan_engine.finish_task_num + self.service_scan_engine.error_task_num,
               self.spend_time,
               self.all_task_num))
        # print('[{}] findish_task_num: {} | error_task_num: {} | remain_task_num: {} | %.2f seconds'
        #       .format(self.source, self.all_task_num, self.service_scan_engine.finish_task_num, self.service_scan_engine.error_task_num,
        #               self.all_task_num - self.service_scan_engine.finish_task_num - self.service_scan_engine.error_task_num, self.spend_time))

    async def _print_progross(self):
        while self._is_continue:
            await asyncio.sleep(60)
            self.print_progross()

    # 慢速扫描模式（弃用）
    # async def spider(self):
    #     task_list = []
    #     semaphore = asyncio.Semaphore(300)
    #     asyncio.ensure_future(self._print_progross())
    #     for target in self.ip_port_list:
    #         self.all_task_num += 1
    #         task = asyncio.create_task(self.slow_scan_bypass_cdn(semaphore, target['ip'], target['port']))
    #         task_list.append(task)
    #     await asyncio.gather(*task_list)
    #     for index in reversed(range(len(self.ip_port_service_list))):
    #         service = self.ip_port_service_list[index].get('service')
    #         ssl_http_list = self.ip_port_service_list[index].get('ip')
    #         if 'ssl' in service or 'http' in service:
    #             if 'http/ssl' in service:
    #                 ssl_http_list = map(lambda s: f'https://{s}', ssl_http_list)
    #             elif 'http' in service:
    #                 ssl_http_list = map(lambda s: f'http://{s}', ssl_http_list)
    #             self.http_ssl_protocol_list.extend(list(ssl_http_list))
    #             self.ip_port_service_list.__delitem__(index)
    #     self.print_progross()
    #     self._is_continue = False
    #     gLogger.myscan_info(self.res_list)
    #     self.write_file(self.res_list, 13)

    # 快扫模式（采用）
    async def spider(self):
        task_list = []
        semaphore = asyncio.Semaphore(500)
        asyncio.ensure_future(self._print_progross())
        for target in self.ip_port_list:

            # 优化扫描速度，如果为内网地址的话就会浪费很多时间
            try:
                if ip_address(target['ip']) and ip_address(target['ip']).is_private:
                    gLogger.myscan_warn('scan host: %s is private, so skip it' % str(target['ip']))
                    continue
            except Exception:
                pass

            for port in target['port']:
                self.all_task_num += 1
                task = asyncio.create_task(self.quick_scan(semaphore, target['ip'], port))
                task_list.append(task)
        await asyncio.gather(*task_list)
        for index in reversed(range(len(self.ip_port_service_list))):
            service = self.ip_port_service_list[index].get('service')
            ssl_http_list = self.ip_port_service_list[index].get('ip')
            if 'ssl' in service or 'http' in service:
                if 'http/ssl' in service:
                    ssl_http_list = map(lambda s: f'https://{s}', ssl_http_list)
                elif 'http' in service:
                    ssl_http_list = map(lambda s: f'http://{s}', ssl_http_list)
                self.http_ssl_protocol_list.extend(list(ssl_http_list))
                self.ip_port_service_list.__delitem__(index)
        self.print_progross()
        self._is_continue = False
        gLogger.myscan_info(self.res_list)
        self.write_file(self.res_list, 12)

    async def main(self):
        await self.spider()
        return self.ip_port_service_list, self.http_ssl_protocol_list


if __name__ == '__main__':
    from core.utils.portwrapper import PortWrapper

    # t = PortWrapper.generate_format('124.221.54.213')
    # PortWrapper.generate_port('top100', t)
    # portscan = PortScan('zjhu.edu.cn', 'aaa', t)
    portscan = PortScan('zjhu.edu.cn', 'aaa', [{'ip': '120.79.66.131', 'port': [3690]}])

    # portscan = PortScan('zjhu.edu.cn', 'aaa', [{'ip': '183.131.122.183', 'port': [9007]}])
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(portscan.main())
    print(res)

