# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-07 20:54

from core.MySetting import top_banner_port
import IPy
from socket import inet_ntoa
from struct import pack


# for port wrapper，用来包装端口的类，默认最低扫描合并TOP100端口加上fofa/quake/shodan，配合异步端口探测
class PortWrapper(object):
    @staticmethod
    def generateFormat(ips):
        # 输入地址段格式
        ipPortList = []
        try:
            if '-' in ips:
                # 这种情况就是 192.168.1.1-192.168.1.255 或者 192.168.1.0-192.168.1.255,192.168.3.0-192.168.3.255
                if ',' in ips:
                    # 192.168.1.0-192.168.1.255,192.168.3.0-192.168.3.255
                    ipSegments = ips.split(',')
                    for ipSegment in ipSegments:
                        ipList = IPy.IP(ipSegment)
                        # print(ipList)
                        for ip in ipList:
                            ipPortList.append({'ip': ip, 'port': []})
                else:
                    # 192.168.1.1-192.168.1.255
                    ipList = IPy.IP(ips)
                    # print(ipList)
                    for ip in ipList:
                        ipPortList.append({'ip': ip, 'port': []})
            elif ',' in ips:
                if '/' in ips:
                    # 192.168.1.0/24,192.168.3.0/24
                    ipSegments = ips.split(',')
                    ipList = []
                    for ipSegment in ipSegments:
                        ipList.extend(IPy.IP(ipSegment))
                    # print(ipList)
                    for ip in ipList:
                        ipPortList.append({'ip': inet_ntoa(pack("!I", ip.int())), 'port': []})
                else:
                    # 192.168.1.1,192.168.1.2
                    ipList = ips.split(',')
                    # print(ipList)
                    for ip in ipList:
                        ipPortList.append({'ip': ip, 'port': []})
            else:
                if '/' in ips:
                    # 192.168.1.0/24
                    ipList = IPy.IP(ips)
                    for ip in ipList:
                        ipPortList.append({'ip': inet_ntoa(pack("!I", ip.int())), 'port': []})
                else:
                    # 192.168.1.1
                    # print(ips)
                    ipPortList.append({'ip': ips, 'port': []})
            # print(ipPortList)
            return ipPortList
        except Exception:
            print('[-] please check your ips format -> {}'.format(ips))
            exit(0)

    @staticmethod
    def parseCommand(ports):
        portList = []
        try:
            # 比如80-9090,70-8080 这种形式的
            if '-' in ports or ',' in ports:
                if len(ports.split('-')) > 2 and len(ports.split(',')) >= 2:
                    portSegments = ports.split(',')
                    for portSegment in portSegments:
                        portStart = portSegment.split('-')[0]
                        portEnd = portSegment.split('-')[1]
                        if int(portEnd) > 65535:
                            print('[-] please check your port format, port not allow big than 65535')
                            exit(0)
                        for port in range(int(portStart), int(portEnd) + 1):
                            portList.append(port)
                # 比如80-9090
                elif len(ports.split('-')) == 2 and ',' not in ports:
                    portStart = ports.split('-')[0]
                    portEnd = ports.split('-')[1]
                    if int(portEnd) > 65535:
                        print('[-] please check your port format, port not allow big than 65535')
                        exit(0)
                    for port in range(int(portStart), int(portEnd) + 1):
                        portList.append(port)
                # 80,90,9090
                elif len(ports.split('-')) == 1 and ',' in ports:
                    portList = ports.split(',')
            elif ports[0:3] == 'top':
                num = int(ports.split('top')[1])
                portList.extend(top_banner_port[0:num])
            else:
                portList.append(ports)
            return portList

            # IP段
            # 比如 192.168.1.1-192.168.1.255
            # pass

            # if len(one.split("-")) == 2:
            #     start_port = int(one.split("-")[0])
            #     end_port = int(one.split("-")[1])
            #     for i in range(start_port, end_port + 1):
            #         if i not in port_list and (0 < i <= 65535):
            #             port_list.append(i)
            # else:
            #     i = int(one)
            #     if i not in port_list and (0 < i <= 65535):
            #         port_list.append(i)
        except Exception as e:
            print('[-] please check your port format, {}'.format(e.__str__()))
            exit(0)

    # generate ports
    @staticmethod
    def generatePorts(ports, ipPortList):
        portList = PortWrapper.parseCommand(ports)
        for index, value in enumerate(ipPortList):
            for i in portList:
                if i not in value['port']:
                    value['port'].append(i)


if __name__ == '__main__':
    test = [{'ip': '202.103.147.144', 'port': [8080, 8090]}, {'ip': '125.19.57.134', 'port': []},
            {'ip': '58.60.230.103', 'port': [8000, 2000]}, {'ip': '202.103.147.169', 'port': [25]}]
    PortWrapper.generatePorts('top100', test)
    print(test)
    # print(top_banner_port[0:100])
