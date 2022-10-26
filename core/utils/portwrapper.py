# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-07 20:54

from core.constant import TOP_1000_BANNER_PORT
from socket import inet_ntoa
from struct import pack
import IPy


# for port wrapper，用来包装端口的类，默认最低扫描合并TOP100端口加上fofa/quake/shodan，配合异步端口探测
class PortWrapper(object):
    @staticmethod
    def generate_format(ips):
        # 输入地址段格式
        ip_port_list = []
        try:
            if isinstance(ips, list):
                for ip in ips:
                    ip_port_list.append({'ip': ip, 'port': []})
            elif '-' in ips:
                # 这种情况就是 192.168.1.1-192.168.1.255 或者 192.168.1.0-192.168.1.255,192.168.3.0-192.168.3.255
                if ',' in ips:
                    # 192.168.1.0-192.168.1.255,192.168.3.0-192.168.3.255
                    ip_segments = ips.split(',')
                    for ip_segment in ip_segments:
                        ip_list = IPy.IP(ip_segment)
                        # print(ipList)
                        for ip in ip_list:
                            ip_port_list.append({'ip': ip, 'port': []})
                else:
                    # 192.168.1.1-192.168.1.255
                    # print(ipList)
                    for ip in IPy.IP(ips):
                        ip_port_list.append({'ip': ip, 'port': []})
            elif ',' in ips:
                if '/' in ips:
                    # 192.168.1.0/24,192.168.3.0/24
                    ip_segments = ips.split(',')
                    ip_list = []
                    for ip_segment in ip_segments:
                        ip_list.extend(IPy.IP(ip_segment))
                    # print(ipList)
                    for ip in ip_list:
                        ip_port_list.append({'ip': inet_ntoa(pack("!I", ip.int())), 'port': []})
                else:
                    # 192.168.1.1,192.168.1.2
                    # print(ipList)
                    for ip in ips.split(','):
                        ip_port_list.append({'ip': ip, 'port': []})
            else:
                if '/' in ips:
                    # 192.168.1.0/24
                    for ip in IPy.IP(ips):
                        ip_port_list.append({'ip': inet_ntoa(pack("!I", ip.int())), 'port': []})
                else:
                    # 192.168.1.1
                    # print(ips)
                    ip_port_list.append({'ip': ips, 'port': []})
            # print(ipPortList)
            return ip_port_list
        except Exception as e:
            print('[-] please check your ips format -> {}, error is {}'.format(ips, e.args))
            exit(0)

    @staticmethod
    def prase_command(ports):
        port_list = []
        try:
            # 比如80-9090,70-8080 这种形式的
            if '-' in ports or ',' in ports:
                if len(ports.split('-')) > 2 and len(ports.split(',')) >= 2:
                    port_segments = ports.split(',')
                    for portSegment in port_segments:
                        port_start = portSegment.split('-')[0]
                        port_end = portSegment.split('-')[1]
                        if int(port_end) > 65535:
                            print('[-] please check your port format, port not allow big than 65535')
                            exit(0)
                        for port in range(int(port_start), int(port_end) + 1):
                            port_list.append(port)
                # 比如80-9090
                elif len(ports.split('-')) == 2 and ',' not in ports:
                    port_start = ports.split('-')[0]
                    port_end = ports.split('-')[1]
                    if int(port_end) > 65535:
                        print('[-] please check your port format, port not allow big than 65535')
                        exit(0)
                    for port in range(int(port_start), int(port_end) + 1):
                        port_list.append(port)
                # 80,90,9090
                elif len(ports.split('-')) == 1 and ',' in ports:
                    port_list = ports.split(',')
            elif ports[0:3] == 'top':
                num = int(ports.split('top')[1])
                port_list.extend(TOP_1000_BANNER_PORT[0:num])
            else:
                port_list.append(ports)
            return port_list
        except Exception as e:
            print('[-] please check your port format, {}'.format(e.__str__()))
            exit(0)

    # generate ports
    @staticmethod
    def generate_port(ports, ip_port_list):
        port_list = PortWrapper.prase_command(ports)
        for index, value in enumerate(ip_port_list):
            for i in port_list:
                if i not in value['port']:
                    value['port'].append(i)


if __name__ == '__main__':
    # lit = [{'ip': '202.103.147.144', 'port': [8080, 8090]}, {'ip': '125.19.57.134', 'port': []},
    #         {'ip': '58.60.230.103', 'port': [8000, 2000]}, {'ip': '202.103.147.169', 'port': [25]}]
    # PortWrapper.generate_port('top100', lit)
    # print(lit)

    lit = PortWrapper.generate_format(['192.168.1.2','192.168.1.3'])
    print(lit)
    print(PortWrapper.generate_port('top100', lit))

    # print(top_banner_port[0:100])
