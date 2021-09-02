# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-02 13:18
import codecs
import contextlib

from spider.BaseSpider import *
from spider.common.banner import *

import zlib

SOCKET_READ_BUFFERSIZE = 1024


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

    def __init__(self, timeout):
        self.sd = None
        self.allprobes = compile_pattern(json.loads(zlib.decompress(base64.b64decode(ALLPROBES))))
        self.all_guess_services = json.loads(zlib.decompress(base64.b64decode(ALL_GUESS_SERVICE)))
        self.timeout = timeout

    async def scan(self, host, port, protocol):
        nmap_fingerprint = {'error': 'unknowservice'}
        in_probes, ex_probes = self.filter_probes_by_port(port, self.allprobes)

        probes = self.sort_probes_by_rarity(in_probes)
        for probe in probes:
            response = self.send_probestring_request(host, port, protocol, probe)
            if response is None:  # 连接超时
                # if self.all_guess_services.get(str(port)) is not None:
                #     return self.all_guess_services.get(str(port))
                # return {'error': 'timeout'}
                continue
            else:
                nmap_service, nmap_fingerprint = self.match_probe_pattern(response, probe)
                if bool(nmap_fingerprint):
                    record = {
                        "service": nmap_service,
                        "versioninfo": nmap_fingerprint,
                    }
                    # ssl特殊处理
                    if nmap_service == "ssl" and self.all_guess_services.get(str(port)) is not None:
                        return self.all_guess_services.get(str(port))
                    return record

        for probe in ex_probes:
            response = self.send_probestring_request(host, port, protocol, probe)
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

    def scan_with_probes(self, host, port, protocol, probes):
        """发送probes中的每个probe到端口."""
        for probe in probes:
            record = self.send_probestring_request(host, port, protocol, probe)
            if bool(record.get('versioninfo')):  # 如果返回了versioninfo信息,表示已匹配,直接返回
                return record
        return {}

    def send_probestring_request(self, host, port, protocol, probe):
        """根据nmap的probestring发送请求数据包"""
        proto = probe['probe']['protocol']
        payload = probe['probe']['probestring']
        payload, _ = codecs.escape_decode(payload)

        response = ""
        # protocol must be match nmap probe protocol
        if proto.upper() == protocol.upper():
            if protocol.upper() == "TCP":
                response = self.send_tcp_request(host, port, payload)
            elif protocol.upper() == "UDP":
                response = self.send_udp_request(host, port, payload)
        return response

    async def send_tcp_request(self, host, port, payload):
        """Send tcp payloads by port number."""
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.settimeout(self.timeout)
            client.connect((host, int(port)))
            client.send(payload)
            data = client.recv(SOCKET_READ_BUFFERSIZE)
            client.close()
        except Exception as e:
            return None
        finally:
            client.close()
        return data

    def send_udp_request(self, host, port, payload):
        """Send udp payloads by port number.
        """
        data = ''
        try:
            with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as client:
                client.settimeout(self.timeout)
                client.sendto(payload, (host, port))
                while True:
                    _, addr = client.recvfrom(SOCKET_READ_BUFFERSIZE)
                    if not _:
                        break
                    data += _
        except Exception as err:
            return None
        return data

    def match_probe_pattern(self, data, probe):
        """Match tcp/udp response based on nmap probe pattern.
        """
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
        except Exception as err:
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
        except Exception as err:
            return nmap_service, nmap_fingerprint
        return nmap_service, nmap_fingerprint

    def match_versioninfo(self, versioninfo):
        """Match Nmap versioninfo
        """

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
        # {'match': {'pattern': '^LO_SERVER_VALIDATING_PIN\\n$',
        #            'service': 'impress-remote',
        #            'versioninfo': ' p/LibreOffice Impress remote/ '
        #                           'cpe:/a:libreoffice:libreoffice/'},
        #  'ports': {'ports': '1599'},
        #  'probe': {'probename': 'LibreOfficeImpressSCPair',
        #            'probestring': 'LO_SERVER_CLIENT_PAIR\\nNmap\\n0000\\n\\n',
        #            'protocol': 'TCP'},
        #  'rarity': {'rarity': '9'}}

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
        """Check port if is in nmap port range
        """
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
        self.timeout = 0.5
        self.serviceScan = ServiceScan(self.timeout)
        self.vulList = []  # {'redis': ['1.1.1.1','2.2.2.2'], 'port': 6379} {'redis': ['3.3.3.3','4.4.4.4'], 'port': 3456}

    def writeFile(self, web_lists, page):
        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(web_lists[index]['ip'])  # scan_ip
            web.append(web_lists[index]['port'])  # port
            web.append(web_lists[index]['service'])  # service
            web.append(web_lists[index]['banner'])  # banner
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(self.domain) + ".xlsx")
        workbook.close()

    async def scan(self, sem, ip, port):
        port = port
        try:
            async with sem:
                sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sd.settimeout(self.timeout)
                sd.connect((ip, port))
                data = await self.serviceScan.scan(ip, port, 'tcp')
                if data.get("error") is None:
                    # self.format_log(self.ip, port, data)
                    self.resList.append({"ip": data.get('ip'), "port": data.get('port'), "service": data.get('service'),
                                         'banner': data.get('banner')})
                    for _ in self.vulList:
                        if _:
                            service = _.get('service')
                            if service == data.get('service'):
                                _['ip'].append('{}:{}'.format(data.get('ip'), data.get('port')))

                    # self.vulList = [{'service': 'redis', 'ip': ['1.1.1.1:6379','2.2.2.2:9874']},
                    # {'service': 'rsync', 'ip': ['3.3.3.3:873','4.4.4.4:783'], }]
                sd.close()
        except Exception as e:
            pass
        finally:
            sd.close()

    async def spider(self):
        for aDict in self.ipPortList:
            pass
            # ipaddress = itodq(host)
            # task = pool.spawn(self.async_scan, ipaddress, port)
            # tasks.append(task)

    async def main(self):
        await self.spider()
        return self.vulList


if __name__ == '__main__':
    alive = PortScan('zjhu.edu.cn', ['120.79.66.58'])
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(alive.main())
    print(res)
