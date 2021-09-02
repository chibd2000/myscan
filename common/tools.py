# coding=utf-8
import xlsxwriter

url_rules = {'.com.cn', '.org.cn', '.net.cn', '.com', '.cn', '.cc', '.net', '.org', '.info', '.fun', '.one', '.xyz',
             '.name', '.io', '.top', '.me', '.club', '.tv', '.uk', '.hk'}

port_rules = {
    'FTP': ['21'],
    'SSH': ['22'],
    'Telnet': ['23'],
    'SMTP': ['25'],
    'DNS': ['53'],
    'DHCP': ['68'],
    'HTTP': ['80', '8080', '81'],
    'TFTP': ['69'],
    'POP3': ['995'],
    'NetBIOS': ['139'],
    'IMAP': ['143'],
    'HTTPS': ['443'],
    'SNMP': ['161'],
    'LDAP': ['489'],
    'SMB': ['445'],
    'SMTPS': ['465'],
    'Linux R RPE': ['512'],
    'Linux R RLT': ['513'],
    'Linux R cmd': ['514'],
    'Rsync': ['873'],
    'IMAPS': ['993'],
    'Proxy': ['1080'],
    'JavaRMI': ['1099'],
    'Lotus': ['1352'],
    'MSSQL': ['1433', '1434'],
    'Oracle': ['1521'],
    'PPTP': ['1723'],
    'cPanel': ['2082'],
    'CPanel': ['2083'],
    'Zookeeper': ['2181'],
    'Docker': ['2375'],
    'Zebra': ['2604'],
    'MySQL': ['3306'],
    'Kangle': ['3312'],
    'RDP': ['3389'],
    'SVN': ['3690'],
    'Rundeck': ['4440'],
    'GlassFish': ['4848'],
    'PostgreSql': ['5432'],
    'PcAnywhere': ['5632'],
    'VNC': ['5900'],
    'CouchDB': ['5984'],
    'varnish': ['6082'],
    'Redis': ['6379'],
    'Weblogic': ['9001'],
    'Kloxo': ['7778'],
    'Zabbix': ['8069', '10050', '10051'],
    'RouterOS': ['8291'],
    'Elasticsearch': ['9200', '9300'],
    'Memcached': ['11211'],
    'MongoDB': ['27017', '28017'],
    'Hadoop': ['50070']
}


def getUrl(domain):
    if 'http://' in domain or 'https://' in domain:
        return f'{domain}'
    else:
        if ':443' in domain:
            return f'https://{domain}'

        if ':80' in domain:
            return f'http://{domain}'

        return f'http://{domain}'


# # 判断a链接的是否为80端口域名
# def getUrl(link):
#     for web_rule in url_rules:
#         if web_rule in link:
#             if 'http' in link:
#                 return link.split(web_rule)[0] + web_rule
#
#                 # # 这里的代码到时候需要改成 写入数据库的代码
#                 # print(link.split(web_rule)[0] + web_rule)


# 列表中的字典 键值重复清理
def getUniqueList(L):
    (output, temp) = ([], [])
    for l in L:
        for k, v in l.items():
            flag = False
            if (k, v) not in temp:
                flag = True
                break
        if flag:
            output.append(l)
        temp.extend(l.items())
    return output


# ip段识别
def getIpSegment(ipList: list):
    ll = []
    for l in ipList:
        l = l.split(".")
        l[-1] = "0/24"
        joinl = ".".join(l)
        if joinl not in ll:
            ll.append(joinl)
    return ll


# 在指定的列表中进行筛选，ip 与 域名 分别放入 两个列表中
def Common_getTwoUniqueList(L):
    pass
    # ip
    # 域名


# 根据port识别服务
def getPortService(port):
    for k, v in port_rules.items():
        for b in v:
            if int(b) == int(port):
                return k
    return 'Unknown'


# 创建图表
def createXlsx(target):
    workbook = xlsxwriter.Workbook(target + ".xlsx")

    worksheet1 = workbook.add_worksheet('备案查询')
    headings1 = ['域名', '主备案号']
    worksheet1.set_column('A:A', 12)
    worksheet1.set_column('B:B', 28)
    worksheet1.write_row('A1', headings1)

    worksheet2 = workbook.add_worksheet('爬虫')
    headings2 = ['爬虫', '关键字', '链接', '标题']  # 设置表头
    worksheet2.set_column('A:A', 7)
    worksheet2.set_column('B:B', 20)
    worksheet2.set_column('C:C', 66)
    worksheet2.set_column('D:D', 60)
    worksheet2.write_row('A1', headings2)

    worksheet3 = workbook.add_worksheet('证书SSL')
    headings3 = ['证书信任域名', '域名']
    worksheet3.set_column('A:A', 24)
    worksheet3.set_column('B:B', 24)
    worksheet3.write_row('A1', headings3)

    worksheet4 = workbook.add_worksheet('子域名A记录')
    headings4 = ['子域名', 'A记录IP']
    worksheet4.set_column('A:A', 40)
    worksheet4.set_column('B:B', 23)
    worksheet4.write_row('A1', headings4)

    worksheet12 = workbook.add_worksheet('IP存活段')
    headings12 = ['IP段分布', '存在IP', '数量']
    worksheet12.set_column('A:A', 19)
    worksheet12.set_column('B:B', 28)
    worksheet12.set_column('C:C', 10)
    worksheet12.write_row('A1', headings12)

    worksheet13 = workbook.add_worksheet('ASN')
    headings13 = ['ASN分布']
    worksheet13.set_column('A:A', 8)
    worksheet13.write_row('A1', headings13)

    worksheet5 = workbook.add_worksheet('ip反查子域名')
    headings5 = ['ip', '域名']
    worksheet5.set_column('A:A', 12)
    worksheet5.set_column('B:B', 28)
    worksheet5.write_row('A1', headings5)

    worksheet6 = workbook.add_worksheet('Fofa')
    headings6 = ['空间引擎名', 'HOST', '标题', 'ip', '子域名', '端口', '服务', '协议', 'asn', '查询语句']
    worksheet6.set_column('A:A', 12)
    worksheet6.set_column('B:B', 28)
    worksheet6.set_column('C:C', 37)
    worksheet6.set_column('D:D', 22)
    worksheet6.set_column('E:E', 17)
    worksheet6.set_column('F:F', 8)
    worksheet6.set_column('G:G', 25)
    worksheet6.set_column('H:H', 8)
    worksheet6.set_column('I:I', 8)
    worksheet6.set_column('J:J', 24)
    worksheet6.write_row('A1', headings6)

    worksheet7 = workbook.add_worksheet('Quake')
    headings7 = ['空间引擎名', 'HOST', '标题', 'ip', '子域名', '端口', '服务', '协议', 'asn', '查询语句']
    worksheet7.set_column('A:A', 12)
    worksheet7.set_column('B:B', 28)
    worksheet7.set_column('C:C', 37)
    worksheet7.set_column('D:D', 22)
    worksheet7.set_column('E:E', 17)
    worksheet7.set_column('F:F', 8)
    worksheet7.set_column('G:G', 25)
    worksheet7.set_column('H:H', 8)
    worksheet7.set_column('I:I', 8)
    worksheet7.set_column('J:J', 24)
    worksheet7.write_row('A1', headings7)

    worksheet8 = workbook.add_worksheet('Shodan')
    headings8 = ['空间引擎名', 'HOST', '标题', 'ip', '子域名', '端口', '服务', '协议', 'asn', '查询语句']
    worksheet8.set_column('A:A', 12)
    worksheet8.set_column('B:B', 28)
    worksheet8.set_column('C:C', 37)
    worksheet8.set_column('D:D', 22)
    worksheet8.set_column('E:E', 17)
    worksheet8.set_column('F:F', 8)
    worksheet8.set_column('G:G', 20)
    worksheet8.set_column('H:H', 8)
    worksheet8.set_column('I:I', 24)
    worksheet8.write_row('A1', headings8)

    worksheet9 = workbook.add_worksheet('子域名端口扫描')
    headings9 = ['ip', '端口', '协议', '服务']
    worksheet9.set_column('A:A', 19)
    worksheet9.set_column('B:B', 28)
    worksheet9.set_column('C:C', 21)
    worksheet9.set_column('D:D', 25)
    worksheet9.write_row('A1', headings9)

    worksheet10 = workbook.add_worksheet('存活网站标题')
    headings10 = ['网址', '状态码', '标题', 'X-Powered-By']
    worksheet10.set_column('A:A', 51)
    worksheet10.set_column('B:B', 10)
    worksheet10.set_column('C:C', 28)
    worksheet10.set_column('D:D', 28)
    worksheet10.write_row('A1', headings10)

    worksheet11 = workbook.add_worksheet('漏洞扫描')
    headings11 = ['漏洞名', 'url', '状态']
    worksheet11.set_column('A:A', 12)
    worksheet11.set_column('B:B', 28)
    worksheet11.set_column('C:C', 28)
    worksheet11.write_row('A1', headings11)

    workbook.close()


# 递归获取父域名
def Common_getTopDomainName(Subdomain, FatherUrl):
    temp_url = FatherUrl.split('.', 1)[1]
    if Subdomain == temp_url:
        return temp_url
    else:
        return Common_getTopDomainName(Subdomain, temp_url)


# 简单的判断下当 端口为443,80的时候返回的格式为http?s:// + ....，否则其他端口的话每个url都返回两次
def Common_url_by_port(domain, port):
    protocols = ['http://', 'https://']
    if port == 443:
        url = f'https://{domain}'
        return url
    elif port == 80:
        url = f'http://{domain}'
        return url
    else:
        url = []
        for protocol in protocols:
            url.append(f'{protocol}{domain}:{port}')
        return url
