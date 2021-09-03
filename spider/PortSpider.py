# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-02 13:18
import codecs
import contextlib

from async_timeout import timeout
from spider.BaseSpider import *
from spider.common.banner import *
import zlib


def compile_pattern(allprobes):
    """编译re的正则表达式"""
    for probe in allprobes:
        matches = probe.get('matches')
        if isinstance(matches, list):
            for match in matches:
                try:
                    # pattern, _ = codecs.escape_decode(match.get('pattern'))
                    pattern = match.get('pattern').encode('utf-8')
                except Exception as err:
                    pass
                try:
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


class ServiceScan(object):

    def __init__(self):
        self.allprobes = compile_pattern(json.loads(zlib.decompress(base64.b64decode(ALLPROBES))))
        self.all_guess_services = json.loads(zlib.decompress(base64.b64decode(ALL_GUESS_SERVICE)))
        self.loop = asyncio.get_event_loop()

    async def scan(self, host, port, protocol):
        nmap_fingerprint = {'error': 'unknowservice'}
        in_probes, ex_probes = self.filter_probes_by_port(port, self.allprobes)
        probes = self.sort_probes_by_rarity(in_probes)
        for probe in probes:
            # print(probe)
            response = await self.send_probestring_request(host, port, protocol, probe)
            # print(response)
            if response is None:  # 连接超时
                # if self.all_guess_services.get(str(port)) is not None:
                #     return self.all_guess_services.get(str(port))
                # return {'error': 'timeout'}
                continue
            else:
                nmap_service, nmap_fingerprint = self.match_probe_pattern(response, probe)
                if bool(nmap_fingerprint):
                    title = ''
                    if 'http' in nmap_service:
                        title = self.get_http_title(response)
                    record = {
                        'ip': host,
                        'port': port,
                        'service': nmap_service,
                        'title': title,
                        'versioninfo': nmap_fingerprint,
                    }
                    # ssl特殊处理
                    if nmap_service == "ssl" and self.all_guess_services.get(str(port)) is not None:
                        return self.all_guess_services.get(str(port))
                    return record

        for probe in ex_probes:
            # print(probe)

            response = await self.send_probestring_request(host, port, protocol, probe)
            # print(response)
            if response is None:  # 连接超时
                # if self.all_guess_services.get(str(port)) is not None:
                #     return self.all_guess_services.get(str(port))
                # return {'error': 'timeout'}
                continue
            else:
                nmap_service, nmap_fingerprint = self.match_probe_pattern(response, probe)
                if bool(nmap_fingerprint):
                    title = ''
                    if b'HTTP' in response and 'http' in nmap_service:
                        title = self.get_http_title(response)
                    record = {
                        'ip': host,
                        'port': port,
                        'service': nmap_service,
                        'title': title,
                        'versioninfo': nmap_fingerprint,
                    }
                    # ssl特殊处理
                    if nmap_service == "ssl" and self.all_guess_services.get(str(port)) is not None:
                        return self.all_guess_services.get(str(port))
                    return record
                else:
                    if self.all_guess_services.get(str(port)) is not None:
                        return self.all_guess_services.get(str(port))
        # 全部检测完成后还没有识别
        if self.all_guess_services.get(str(port)) is not None:
            return self.all_guess_services.get(str(port))
        else:
            return {'error': 'unknowservice'}

    async def scan_with_probes(self, host, port, protocol, probes):
        """发送probes中的每个probe到端口."""
        for probe in probes:
            record = await self.send_probestring_request(host, port, protocol, probe)
            if bool(record.get('versioninfo')):  # 如果返回了versioninfo信息,表示已匹配,直接返回
                return record
        return {}

    async def send_probestring_request(self, host, port, protocol, probe):
        """根据nmap的probestring发送请求数据包"""
        # {
        #   'match': {'pattern': '^LO_SERVER_VALIDATING_PIN\\n$', 'service': 'impress-remote', 'versioninfo': ' p/LibreOffice Impress remote/ '
        #                           'cpe:/a:libreoffice:libreoffice/'},
        #   'ports': {'ports': '1599'},
        #   'probe': {'probename': 'LibreOfficeImpressSCPair',
        #            'probestring': 'LO_SERVER_CLIENT_PAIR\\nNmap\\n0000\\n\\n',
        #            'protocol': 'TCP'},
        #   'rarity': {'rarity': '9'}
        #  }
        proto = probe['probe']['protocol']
        payload = probe['probe']['probestring']
        payload, _ = codecs.escape_decode(payload)

        response = ""
        # protocol must be match nmap probe protocol
        if proto.upper() == protocol.upper():
            if protocol.upper() == "TCP":
                response = await self.send_tcp_request(host, port, payload)
            elif protocol.upper() == "UDP":
                response = await self.send_udp_request(host, port, payload)
        return response

    async def send_tcp_request(self, host, port, payload):
        """Send tcp payloads by port number."""
        try:
            with timeout(1):
                reader, writer = await asyncio.open_connection(host, port)
                writer.write(payload)
                await writer.drain()
                data = await reader.read(1024)
                return data
        except Exception as e:
            return None
        finally:
            writer.close()

    # not async
    def send_udp_request(self, host, port, payload):
        """Send udp payloads by port number."""
        data = ''
        try:
            with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as client:
                client.settimeout(0.7)
                client.sendto(payload, (host, port))
                while True:
                    _, addr = client.recvfrom(1024)
                    if not _:
                        break
                    data += _
        except Exception as err:
            return None
        return data

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

                    nmap_fingerprint = self.match_versioninfo(versioninfo)
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

    def match_versioninfo(self, versioninfo):
        """Match Nmap versioninfo"""

        record = {
            "vendorproductname": [],
            "version": [],
            "info": [],
            "hostname": [],
            "operatingsystem": [],
            "cpename": []
        }

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
        if record == {"vendorproductname": [], "version": [], "info": [], "hostname": [], "operatingsystem": [],
                      "cpename": []}:
            return None
        return record

    def sort_probes_by_rarity(self, probes):
        """Sorts by rarity
        """
        newlist = sorted(probes, key=lambda k: k['rarity']['rarity'])
        return newlist

    def filter_probes_by_port(self, port, probes):
        """通过端口号进行过滤,返回强符合的probes和弱符合的probes"""
        # {
        #   'match': {'pattern': '^LO_SERVER_VALIDATING_PIN\\n$', 'service': 'impress-remote', 'versioninfo': ' p/LibreOffice Impress remote/ '
        #                           'cpe:/a:libreoffice:libreoffice/'},
        #   'ports': {'ports': '1599'},
        #   'probe': {'probename': 'LibreOfficeImpressSCPair',
        #            'probestring': 'LO_SERVER_CLIENT_PAIR\\nNmap\\n0000\\n\\n',
        #            'protocol': 'TCP'},
        #   'rarity': {'rarity': '9'}
        #  }

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

    def get_http_title(self, response):
        title = '获取失败'
        try:
            title_pattern = b'<title>(.*?)</title>'
            title = re.search(title_pattern, response, re.S | re.I).group(1)
            try:
                title = title.decode().replace('\n', '').strip()
                return title
            except:
                try:
                    title = title.decode('gbk').replace('\n', '').strip()
                    return title
                except:
                    return title
        except:
            return title
        finally:
            if title == '':
                return title + ' 标题为空'
            else:
                return title


class PortScan(Spider):
    def __init__(self, domain, ipPortList):
        super().__init__()
        self.domain = domain
        self.ipPortList = ipPortList
        self.loop = asyncio.get_event_loop()
        self.serviceScan = ServiceScan()
        self.ipPortServiceList = []

    def writeFile(self, web_lists, page):
        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(str(web_lists[index]['ip']))  # scan_ip
            web.append(str(web_lists[index]['port']))  # port
            web.append(str(web_lists[index]['service']))  # service
            web.append(str(web_lists[index]['title']))  # service
            web.append(str(web_lists[index]['versioninfo']))  # versioninfo
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(self.domain) + ".xlsx")
        workbook.close()

    async def scan(self, semaphore, ip, port):
        async with semaphore:
            try:
                # with timeout(0.7):
                #     reader, writer = await asyncio.open_connection(ip, port)
                #     print(reader, writer)
                #     writer.close()
                # sock.settimeout(0.7)
                # sock.connect((ip, int(port)))
                data = await self.serviceScan.scan(ip, port, 'tcp')
                if data.get('error') is None:
                    # self.format_log(self.ip, port, data)
                    self.resList.append({'ip': ip, 'port': port, 'service': data.get('service'), 'title': data.get('title'), 'versioninfo': data.get('versioninfo')})
                    print(data)
                    # for i in self.vulList:
                    #     if i['service'] ==
                    flag = True
                    for _ in self.ipPortServiceList:
                        if _:
                            service = _.get('service')
                            if service == data.get('service'):
                                flag = False
                                _['ip'].append('{}:{}'.format(ip, port))
                    if flag:
                        self.ipPortServiceList.append({'service': str(data.get('service')), 'ip': ['{}:{}'.format(ip, port)]})
                    # self.vulList = [{'service': 'redis', 'ip': ['1.1.1.1:6379','2.2.2.2:9874']},
                    # {'service': 'rsync', 'ip': ['3.3.3.3:873','4.4.4.4:783'], }]
            except Exception as e:
                pass

    async def spider(self):
        semaphore = asyncio.Semaphore(500)
        taskList = []
        for aDict in self.ipPortList:
            for port in aDict['port']:
                ip = aDict['ip']
                task = asyncio.create_task(self.scan(semaphore, ip, port))
                taskList.append(task)
        await asyncio.gather(*taskList)
        self.writeFile(self.resList, 10)

    async def main(self):
        await self.spider()
        return self.ipPortServiceList  # 返回需要探测的端口服务,剩下的交给Exploit模块
    # self.vulList = [
    # {'service': 'redis', 'ip': ['1.1.1.1:6379','2.2.2.2:9874']},
    # {'service': 'rsync', 'ip': ['3.3.3.3:873','4.4.4.4:783'], }
    # ]


if __name__ == '__main__':
    portscan = PortScan('zjhu.edu.cn', [{'ip': '61.153.52.21', 'port': [5001, 5008]},
                                        {'ip': '61.153.52.74', 'port': []},
                                        {'ip': '61.153.52.24', 'port': []}, {'ip': '61.153.52.23', 'port': []}, {'ip': '61.153.52.57', 'port': [4430]}, {'ip': '61.153.52.52', 'port': [4430, 4430]}, {'ip': '61.153.52.68', 'port': []}, {'ip': '61.153.52.20', 'port': [4433, 4433, 4433, 4433, 4433]}, {'ip': '211.80.146.57', 'port': [4430]}, {'ip': '211.80.146.74', 'port': []}, {'ip': '61.153.52.103', 'port': []}, {'ip': '61.153.52.11', 'port': []}, {'ip': '61.153.52.15', 'port': []}, {'ip': '61.153.52.48', 'port': []}, {'ip': '114.255.40.175', 'port': []}, {'ip': '61.153.52.10', 'port': []}, {'ip': '123.58.177.239', 'port': []}, {'ip': '61.153.52.78', 'port': []}, {'ip': '61.153.52.46', 'port': [8080]}, {'ip': '221.12.135.204', 'port': []}, {'ip': '61.153.52.62', 'port': []}, {'ip': '221.12.135.208', 'port': []}, {'ip': '61.153.52.31', 'port': []}, {'ip': '61.153.52.42', 'port': []}, {'ip': '120.199.142.57', 'port': [4430]}, {'ip': '120.199.142.74', 'port': []}, {'ip': '61.153.52.83', 'port': []}, {'ip': '120.199.142.40', 'port': []}, {'ip': '61.153.52.40', 'port': []}, {'ip': '61.153.52.64', 'port': []}, {'ip': '211.80.146.40', 'port': []}, {'ip': '61.153.52.32', 'port': []}, {'ip': '61.153.52.18', 'port': []}, {'ip': '221.12.135.197', 'port': [4430]}, {'ip': '221.12.135.210', 'port': []}, {'ip': '120.199.142.46', 'port': [8080]}, {'ip': '61.153.52.9', 'port': [8888]}, {'ip': '211.80.146.1', 'port': [8888]}, {'ip': '61.153.52.63', 'port': []}, {'ip': '61.153.52.12', 'port': []}, {'ip': '221.12.135.200', 'port': []}, {'ip': '61.153.52.37', 'port': []}, {'ip': '120.199.142.78', 'port': []}, {'ip': '221.12.135.212', 'port': []}, {'ip': '221.12.135.217', 'port': []}, {'ip': '211.80.146.62', 'port': []}, {'ip': '120.199.142.11', 'port': []}, {'ip': '61.153.52.84', 'port': []}])
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(portscan.main())
    print(res)
