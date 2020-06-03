# coding=utf-8

# from Spider.BaseSpider import *
import nmap
import multiprocessing
import json
import openpyxl
import os
import requests
import re
import chardet
requests.packages.urllib3.disable_warnings()

abs_path = os.getcwd() + os.path.sep

# 端口扫描的实现
class PortScan(object):
    def __init__(self, domain, _ip):
        self.domain = domain
        self.scanlists = []
        self.ports = []
        self._ip = _ip

    # 写文件操作
    def write_file(self, web_lists, target, page):
        workbook = openpyxl.load_workbook(abs_path + str(target) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(web_lists[index]['scan_ip'])  # scan_ip
            web.append(web_lists[index]['port'])  # port
            web.append(web_lists[index]['banner'])  # banner
            web.append(web_lists[index]['service_name'])  # service
            web.append(web_lists[index]['title'])  # title
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(target) + ".xlsx")
        workbook.close()

    # 调用masscan识别端口
    def Portscan(self, scan_ip):
        temp_ports = []  # 设定一个临时端口列表
        os.system(abs_path + 'masscan.exe ' + scan_ip + ' -p 1-65535 -oJ masscan' + str(scan_ip) + '.json --rate 1000')

        # 提取json文件中的端口
        with open(abs_path + 'masscan' + str(scan_ip) + '.json', 'r') as f:
            for line in f:
                if line.startswith('{ '):
                    temp = json.loads(line[:-2])  # 取出一条完整json形式的数据
                    temp_ports.append(str(temp["ports"][0]["port"]))# 端口取出加入临时端口中

        if len(temp_ports) > 25:
            print("判断防火墙存在 结束当前进程!")
            # temp_ports.clear()  # 如果端口数量大于25，说明可能存在防火墙，属于误报，清空列表
            exit(0)
        else:
            self.ports.extend(temp_ports)  # 小于30则放到总端口列表里

    # 调用nmap识别服务
    def Scan(self, scan_ip):
        nm = nmap.PortScanner()
        try:
            for port in self.ports:
                info = {}  # 存储字典
                ret = nm.scan(scan_ip, port, arguments='-Pn -sS')  # 默认是 not ping 半tcp策略扫描
                service_name = ret['scan'][scan_ip]['tcp'][int(port)]['name']
                # print('[*] 主机 ' + scan_ip + ' 的 ' + str(port) + ' 端口服务为: ' + service_name)

                # 一共有三种情况 一种是http 一种是https 一种是 不是http 不是https

                # 如果扫描出来的协议是https的话则如下操作
                if 'http' in service_name or service_name == 'sun-answerbook':
                    if service_name == 'https' or service_name == 'https-alt':
                        scan_url_port = 'https://' + scan_ip + ':' + str(port)
                        info['scan_ip'] = scan_ip
                        info['service_name'] = service_name
                        info['port'] = port
                        try:
                            resp = requests.get(scan_url_port, timeout=3, verify=False)
                            # 获取网站的页面编码并且应用
                            detectencode = chardet.detect(resp.content)  # 利用chardet模块检测编码
                            response = re.findall(r'<title>(.*?)</title>', resp.content.decode(detectencode['encoding']), re.S)  # re.S的作用 匹配的时候扩展到整个字符串(包括换行这些\n)
                            if response:  # 如果访问的时候正则匹配到<title>标签
                                # 将页面解码为utf-8，获取中文标题
                                # 如果访问的时候正则匹配到title标签
                                title = response[0]
                                banner = resp.headers['server']
                                info['banner'] = banner
                                info['title'] = title
                            else:
                                info['banner'] = ''
                                info['title'] = ''
                            self.scanlists.append(info)
                            # print(info)
                        except:
                            pass
                    else:
                        # 探测为http协议的时候
                        scan_url_port = 'http://' + scan_ip + ':' + str(port)
                        info['scan_ip'] = scan_ip
                        info['service_name'] = service_name
                        info['port'] = port
                        try:
                            # 获取标题
                            resp = requests.get(scan_url_port, timeout=3, verify=False)
                            # 获取网站的页面编码并且应用
                            detectencode = chardet.detect(resp.content)  # 利用chardet模块检测编码
                            response = re.findall(r'<title>(.*?)</title>', resp.content.decode(detectencode['encoding']), re.S)  # re.S的作用 匹配的时候扩展到整个字符串(包括换行这些\n)
                            if response:  # 如果访问的时候正则匹配到<title>标签
                                # 将页面解码为utf-8，获取中文标题
                                # 如果访问的时候正则匹配到title标签
                                title = response[0]
                                banner = resp.headers['server']
                                # self.scanlists.append(scan_url_port + '\t' + banner + '\t' + title)
                                info['banner'] = banner
                                info['title'] = title
                            else:
                                # self.scanlists.append(scan_url_port + '\t' + service_name + '\t' + "获取标题失败，请手动尝试！！！")
                                info['banner'] = ''
                                info['title'] = ''
                            self.scanlists.append(info)
                            # print(info)
                        except:
                            pass
                # 如果不是 http https则为其他端口默认http请求访问探测
                else:
                    # 形式为：["47.96.196.217:443    https","47.96.196.217:80    blackice-icecap"]....
                    info['banner'] = ''
                    info['title'] = ''
                    info['scan_ip'] = scan_ip
                    info['port'] = port
                    info['service_name'] = service_name
                    self.scanlists.append(info)
                    # print(info)
                    # self.scanlists.append(scan_ip + ':' + str(port) + '\t端口服务为: ' + service_name)
        except Exception as e:
            print(e)
            pass
        self.ports.clear()  # 扫一次清理一次

    def main(self):
        print("当前正在扫描的IP为：" + self._ip)
        self.Portscan(self._ip)
        self.Scan(self._ip)
        self.write_file(self.scanlists, self.domain, 5)


if __name__ == '__main__':
    clear_task_list = [
        {'subdomain': '', 'ips': '60.190.19.102', 'port': [], 'target': 'ip'},
        {'subdomain': 'webvpn.nbcc.cn', 'ips': '42.247.33.26', 'port': None, 'target': 'subdomain'},
        {'subdomain': 'a004.cache.saaswaf.com', 'ips': '119.188.95.114', 'port': None, 'target': 'webdomain'},
        {'subdomain': 'vpn.nbcc.cn', 'ips': '42.247.33.25', 'port': None, 'target': 'subdomain'},
        {'subdomain': 'vpan.nbcc.cn', 'ips': '120.79.66.58', 'port': None, 'target': 'subdomain'},
        {'subdomain': 'vpsn.nbcc.cn', 'ips': '42.247.33.25', 'port': None, 'target': 'subdomain'},
        {'subdomain': 'vpsn.nbcc.cn', 'ips': '47.56.199.16', 'port': None, 'target': 'subdomain'},
        {'subdomain': 'vpsn.nbcc.cn', 'ips': '116.85.41.113', 'port': None, 'target': 'subdomain'}

    ]

    multiprocessing.freeze_support()
    temp_ips = []  # 用来记录扫描过的ip 防止多次扫描 节省时间
    pool = multiprocessing.Pool(5)
    for aaa in clear_task_list:
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
                    bbb = PortScan('nbcc.cn', aaa['ips'])
                    pool.apply_async(func=bbb.main)  # 异步运行,非阻塞
    pool.close()
    pool.join()