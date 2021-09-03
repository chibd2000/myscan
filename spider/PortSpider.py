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
                    record = {
                        'ip': host,
                        'port': port,
                        'service': nmap_service,
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
                    record = {
                        "ip": host,
                        "port": port,
                        "service": nmap_service,
                        "banner": nmap_fingerprint,
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


class PortScan(Spider):
    def __init__(self, domain, ipPortList):
        super().__init__()
        self.domain = domain
        self.ipPortList = ipPortList
        self.loop = asyncio.get_event_loop()
        self.serviceScan = ServiceScan()
        self.vulList = []

    def writeFile(self, web_lists, page):
        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(str(web_lists[index]['ip']))  # scan_ip
            web.append(str(web_lists[index]['port']))  # port
            web.append(str(web_lists[index]['service']))  # service
            # web.append(str(web_lists[index]['banner']))  # banner
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
                    self.resList.append({'ip': ip, 'port': port, 'service': data.get('service')})
                    print(data)
                    # for i in self.vulList:
                    #     if i['service'] ==

                    flag = True
                    for _ in self.vulList:
                        if _:
                            service = _.get('service')
                            if service == data.get('service'):
                                flag = False
                                _['ip'].append('{}:{}'.format(ip, port))
                    if flag:
                        self.vulList.append({'service': str(data.get('service')), 'ip': ['{}:{}'.format(ip, port)]})
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
        return self.vulList  # 返回需要探测的端口服务,剩下的交给Exploit模块
    # self.vulList = [
    # {'service': 'redis', 'ip': ['1.1.1.1:6379','2.2.2.2:9874']},
    # {'service': 'rsync', 'ip': ['3.3.3.3:873','4.4.4.4:783'], }
    # ]


if __name__ == '__main__':
    portscan = PortScan('zjhu.edu.cn', [{'ip': '127.0.0.1', 'port': [6377]}, {'ip': '125.19.57.134', 'port': []},
                                        {'ip': '58.60.230.103', 'port': [8000, 2000]},
                                        {'ip': '202.103.147.169', 'port': [25]}, {'ip': '125.19.57.136', 'port': []},
                                        {'ip': '58.60.230.102', 'port': [179]}, {'ip': '209.9.37.38', 'port': [25]},
                                        {'ip': '63.217.80.70', 'port': [25]}, {'ip': '202.103.147.161', 'port': [25]},
                                        {'ip': '103.27.119.242', 'port': [541]},
                                        {'ip': '202.103.147.172', 'port': [25]}, {'ip': '125.19.57.132', 'port': []},
                                        {'ip': '218.2.178.14', 'port': []}, {'ip': '119.23.244.247', 'port': []},
                                        {'ip': '61.132.54.28', 'port': []}, {'ip': '210.21.223.9', 'port': [8080]},
                                        {'ip': '149.129.151.100', 'port': [8443, 8080]},
                                        {'ip': '47.110.217.169', 'port': [8443, 8080]},
                                        {'ip': '47.106.97.155', 'port': []},
                                        {'ip': '47.254.137.137', 'port': [8443, 8080]},
                                        {'ip': '41.169.101.13', 'port': [8080]}, {'ip': '4.14.239.109', 'port': []},
                                        {'ip': '58.251.27.73', 'port': [8080, '9000']},
                                        {'ip': '58.60.230.115', 'port': [8080]}, {'ip': '210.21.236.181', 'port': []},
                                        {'ip': '63.221.140.244', 'port': [8080]}, {'ip': '112.74.28.147', 'port': []},
                                        {'ip': '61.132.54.33', 'port': []}, {'ip': '63.221.140.237', 'port': [8080]},
                                        {'ip': '58.251.27.72', 'port': []}, {'ip': '113.98.59.166', 'port': [8080]},
                                        {'ip': '61.54.1.23', 'port': [8080]}, {'ip': '210.74.157.110', 'port': []},
                                        {'ip': '209.9.37.59', 'port': [8080]}, {'ip': '58.60.230.71', 'port': []},
                                        {'ip': '58.60.230.23', 'port': []}, {'ip': '210.51.195.20', 'port': []},
                                        {'ip': '4.14.134.163', 'port': [8080]},
                                        {'ip': '200.196.255.15', 'port': [8080]}, {'ip': '205.252.217.110', 'port': []},
                                        {'ip': '113.98.59.188', 'port': []}, {'ip': '113.140.11.236', 'port': []},
                                        {'ip': '116.228.53.166', 'port': []}, {'ip': '113.140.11.173', 'port': []},
                                        {'ip': '119.188.176.41', 'port': []}, {'ip': '112.65.203.41', 'port': []},
                                        {'ip': '41.169.101.12', 'port': [8080]}, {'ip': '209.9.37.60', 'port': [8080]},
                                        {'ip': '200.196.255.14', 'port': []}, {'ip': '210.21.223.8', 'port': []},
                                        {'ip': '63.221.140.249', 'port': []}, {'ip': '210.21.236.140', 'port': []},
                                        {'ip': '202.103.147.168', 'port': []}, {'ip': '47.113.23.213', 'port': [8080]},
                                        {'ip': '222.134.66.177', 'port': [8080]}, {'ip': '59.83.221.136', 'port': []},
                                        {'ip': '113.195.63.4', 'port': []}, {'ip': '123.125.132.41', 'port': []},
                                        {'ip': '61.54.7.71', 'port': [8080]}, {'ip': '153.3.231.195', 'port': []},
                                        {'ip': '139.199.64.205', 'port': [8080]}, {'ip': '163.181.37.207', 'port': []},
                                        {'ip': '59.83.221.131', 'port': []}, {'ip': '222.134.66.167', 'port': []},
                                        {'ip': '222.134.66.173', 'port': [8080]},
                                        {'ip': '222.134.66.172', 'port': [8000, 8888]},
                                        {'ip': '59.83.221.137', 'port': [8888]}, {'ip': '61.54.7.72', 'port': []},
                                        {'ip': '59.83.221.134', 'port': [8080]},
                                        {'ip': '222.134.66.180', 'port': [8000]},
                                        {'ip': '222.134.66.166', 'port': [8888]}, {'ip': '61.54.7.74', 'port': [8000]},
                                        {'ip': '47.52.122.123', 'port': [8443]}, {'ip': '34.225.11.109', 'port': []},
                                        {'ip': '8.209.73.231', 'port': []}, {'ip': '8.209.75.179', 'port': []},
                                        {'ip': '8.136.203.6', 'port': []}, {'ip': '8.136.192.28', 'port': []},
                                        {'ip': '3.127.130.125', 'port': []}, {'ip': '47.96.196.50', 'port': [8443]},
                                        {'ip': '52.66.15.8', 'port': []}, {'ip': '42.228.133.155', 'port': []},
                                        {'ip': '47.254.137.126', 'port': [8443]}, {'ip': '162.62.21.177', 'port': []},
                                        {'ip': '162.62.175.82', 'port': []}, {'ip': '162.62.175.36', 'port': []},
                                        {'ip': '162.62.177.226', 'port': []}, {'ip': '47.254.4.109', 'port': [8443]},
                                        {'ip': '47.114.57.137', 'port': []}, {'ip': '52.3.86.87', 'port': []},
                                        {'ip': '113.140.11.179', 'port': []}, {'ip': '47.98.215.180', 'port': []},
                                        {'ip': '163.181.33.225', 'port': []}, {'ip': '120.77.205.232', 'port': []},
                                        {'ip': '47.114.44.220', 'port': []}, {'ip': '47.98.16.135', 'port': []},
                                        {'ip': '115.29.211.225', 'port': []}, {'ip': '120.77.238.227', 'port': []},
                                        {'ip': '120.78.230.242', 'port': []}, {'ip': '54.166.86.130', 'port': []},
                                        {'ip': '52.66.18.225', 'port': []}, {'ip': '52.59.150.47', 'port': []},
                                        {'ip': '52.20.89.141', 'port': []}, {'ip': '47.108.157.149', 'port': []},
                                        {'ip': '47.114.162.115', 'port': []}, {'ip': '39.98.182.209', 'port': []},
                                        {'ip': '162.62.34.107', 'port': []}, {'ip': '47.113.54.67', 'port': []},
                                        {'ip': '119.23.51.233', 'port': []}, {'ip': '39.98.197.84', 'port': []},
                                        {'ip': '13.234.203.51', 'port': []}, {'ip': '218.2.178.21', 'port': []},
                                        {'ip': '120.24.93.16', 'port': []}, {'ip': '47.107.72.66', 'port': []},
                                        {'ip': '35.157.243.178', 'port': []}, {'ip': '47.102.129.5', 'port': []},
                                        {'ip': '52.57.138.198', 'port': []}, {'ip': '52.57.159.2', 'port': []},
                                        {'ip': '120.26.62.125', 'port': []}, {'ip': '121.40.53.175', 'port': []},
                                        {'ip': '18.159.114.210', 'port': []}, {'ip': '47.244.25.148', 'port': []},
                                        {'ip': '52.201.38.101', 'port': []}, {'ip': '34.225.0.168', 'port': []},
                                        {'ip': '54.197.161.80', 'port': []}, {'ip': '120.25.175.158', 'port': []},
                                        {'ip': '121.40.138.88', 'port': []}, {'ip': '121.40.161.9', 'port': []},
                                        {'ip': '121.199.5.96', 'port': []}, {'ip': '121.199.6.126', 'port': []},
                                        {'ip': '120.78.194.86', 'port': []}, {'ip': '121.43.34.117', 'port': []},
                                        {'ip': '120.27.16.1', 'port': []}, {'ip': '120.55.37.69', 'port': []},
                                        {'ip': '120.27.150.207', 'port': []}, {'ip': '115.29.204.124', 'port': []},
                                        {'ip': '114.55.109.116', 'port': []}, {'ip': '114.55.57.81', 'port': []},
                                        {'ip': '114.55.41.10', 'port': []}, {'ip': '106.14.127.244', 'port': []},
                                        {'ip': '101.37.160.198', 'port': []}, {'ip': '101.37.22.242', 'port': []},
                                        {'ip': '47.114.104.80', 'port': []}, {'ip': '47.97.206.253', 'port': []},
                                        {'ip': '47.74.244.141', 'port': []}, {'ip': '39.98.242.191', 'port': []},
                                        {'ip': '47.91.90.92', 'port': []}, {'ip': '39.98.88.177', 'port': []},
                                        {'ip': '39.98.180.11', 'port': []}, {'ip': '47.100.166.67', 'port': []},
                                        {'ip': '47.92.49.128', 'port': []}, {'ip': '47.74.188.175', 'port': []},
                                        {'ip': '8.210.67.100', 'port': [8443, '8443']},
                                        {'ip': '47.253.3.132', 'port': []}, {'ip': '47.111.170.47', 'port': []},
                                        {'ip': '47.110.225.118', 'port': []}, {'ip': '34.230.237.154', 'port': []},
                                        {'ip': '121.196.123.97', 'port': []}, {'ip': '163.181.37.188', 'port': []},
                                        {'ip': '118.212.225.122', 'port': []}, {'ip': '47.106.170.128', 'port': []},
                                        {'ip': '113.106.97.139', 'port': []}, {'ip': '113.98.59.181', 'port': []},
                                        {'ip': '113.140.11.199', 'port': []}, {'ip': '114.215.253.188', 'port': []},
                                        {'ip': '3.231.192.77', 'port': []}, {'ip': '8.135.110.32', 'port': []},
                                        {'ip': '47.252.13.196', 'port': []}, {'ip': '18.184.132.222', 'port': []},
                                        {'ip': '15.207.151.187', 'port': []}, {'ip': '52.55.115.112', 'port': []},
                                        {'ip': '210.51.195.51', 'port': []}, {'ip': '8.129.71.44', 'port': []},
                                        {'ip': '39.96.250.241', 'port': []}, {'ip': '47.113.22.231', 'port': []},
                                        {'ip': '120.25.234.122', 'port': []}, {'ip': '116.62.43.88', 'port': []},
                                        {'ip': '47.97.9.205', 'port': []}, {'ip': '47.98.31.14', 'port': []},
                                        {'ip': '18.233.49.167', 'port': []}, {'ip': '101.37.134.103', 'port': []},
                                        {'ip': '47.107.165.27', 'port': []}, {'ip': '210.51.195.49', 'port': []},
                                        {'ip': '112.74.174.146', 'port': []}, {'ip': '47.100.61.202', 'port': []},
                                        {'ip': '120.24.26.72', 'port': []}])
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(portscan.main())
    print(res)
