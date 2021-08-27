# coding=utf-8
import xlsxwriter
import re
import os

abs_path = os.getcwd() + os.path.sep

url_rules = {'.com.cn', '.org.cn', '.net.cn', '.com', '.cn', '.cc', '.net', '.org', '.info', '.fun', '.one', '.xyz',
             '.name', '.io', '.top', '.me', '.club', '.tv', '.uk', '.hk'}

port_rules = {
    'FTP': '21',
    'SSH': '22',
    'Telnet': '23',
    'SMTP': '25',
    'DNS': '53',
    'DHCP': '68',
    'HTTP': '80',
    'TFTP': '69',
    'HTTP': '8080',
    'POP3': '995',
    'NetBIOS': '139',
    'IMAP': '143',
    'HTTPS': '443',
    'SNMP': '161',
    'LDAP': '489',
    'SMB': '445',
    'SMTPS': '465',
    'Linux R RPE': '512',
    'Linux R RLT': '513',
    'Linux R cmd': '514',
    'Rsync': '873',
    'IMAPS': '993',
    'Proxy': '1080',
    'JavaRMI': '1099',
    'Lotus': '1352',
    'MSSQL': '1433',
    'MSSQL': '1434',
    'Oracle': '1521',
    'PPTP': '1723',
    'cPanel': '2082',
    'CPanel': '2083',
    'Zookeeper': '2181',
    'Docker': '2375',
    'Zebra': '2604',
    'MySQL': '3306',
    'Kangle': '3312',
    'RDP': '3389',
    'SVN': '3690',
    'Rundeck': '4440',
    'GlassFish': '4848',
    'PostgreSql': '5432',
    'PcAnywhere': '5632',
    'VNC': '5900',
    'CouchDB': '5984',
    'varnish': '6082',
    'Redis': '6379',
    'Weblogic': '9001',
    'Kloxo': '7778',
    'Zabbix': '8069',
    'RouterOS': '8291',
    'Elasticsearch': '9200',
    'Elasticsearch': '9300',
    'Zabbix': '10050',
    'Zabbix': '10051',
    'Memcached': '11211',
    'MongoDB': '27017',
    'MongoDB': '28017',
    'Hadoop': '50070'
}

# 判断a链接的是否为80端口域名
def Common_getUrl(link):
    for web_rule in url_rules:
        if web_rule in link:
            if 'http' in link:
                return link.split(web_rule)[0] + web_rule

                # # 这里的代码到时候需要改成 写入数据库的代码
                # print(link.split(web_rule)[0] + web_rule)


# 列表中的字典 键值重复清理
def Common_getUniqueList(L):
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
def Common_getIpSegment(L):
    ll = []
    for l in L:
        l = l.split(".")
        l[-1] = "0"
        joinl = ".".join(l)
        if (joinl not in ll):
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
        if v == port:
            return k
    return 'Unknown'


# 创建图表
def Common_createXlxs(target):
    workbook = xlsxwriter.Workbook(target + ".xlsx")

    worksheet1 = workbook.add_worksheet('爬虫')
    headings1 = ['爬虫', '关键字', '链接', '标题']  # 设置表头
    worksheet1.set_column('A:A', 7)
    worksheet1.set_column('B:B', 20)
    worksheet1.set_column('C:C', 66)
    worksheet1.set_column('D:D', 60)
    worksheet1.write_row('A1', headings1)

    worksheet2 = workbook.add_worksheet('证书SSL')
    headings2 = ['证书信任域名', '域名']
    worksheet2.set_column('A:A', 24)
    worksheet2.set_column('B:B', 24)
    worksheet2.write_row('A1', headings2)

    worksheet3 = workbook.add_worksheet('子域名A记录')
    headings3 = ['子域名', 'A记录IP']
    worksheet3.set_column('A:A', 40)
    worksheet3.set_column('B:B', 23)
    worksheet3.write_row('A1', headings3)

    worksheet4 = workbook.add_worksheet('Fofa空间搜索引擎')
    headings4 = ['空间引擎名', 'HOST', '标题', 'ip', '子域名', '端口', '服务', '协议', '查询语句']
    worksheet4.set_column('A:A', 12)
    worksheet4.set_column('B:B', 28)
    worksheet4.set_column('C:C', 37)
    worksheet4.set_column('D:D', 22)
    worksheet4.set_column('E:E', 17)
    worksheet4.set_column('F:F', 8)
    worksheet4.set_column('G:G', 25)
    worksheet4.set_column('H:H', 8)
    worksheet4.set_column('I:I', 24)
    worksheet4.write_row('A1', headings4)

    worksheet5 = workbook.add_worksheet('Shodan空间搜索引擎')
    headings5 = ['空间引擎名', 'HOST', '标题', 'ip', '子域名', '端口', '服务', '协议', '查询语句']
    worksheet5.set_column('A:A', 12)
    worksheet5.set_column('B:B', 28)
    worksheet5.set_column('C:C', 37)
    worksheet5.set_column('D:D', 22)
    worksheet5.set_column('E:E', 17)
    worksheet5.set_column('F:F', 8)
    worksheet5.set_column('G:G', 20)
    worksheet5.set_column('H:H', 8)
    worksheet5.set_column('I:I', 24)
    worksheet5.write_row('A1', headings5)

    worksheet6 = workbook.add_worksheet('子域名端口扫描')
    headings6 = ['ip', '端口', '协议', '服务', '标题']
    worksheet6.set_column('A:A', 19)
    worksheet6.set_column('B:B', 28)
    worksheet6.set_column('C:C', 21)
    worksheet6.set_column('D:D', 25)
    worksheet6.set_column('E:E', 20)
    worksheet6.write_row('A1', headings6)

    worksheet7 = workbook.add_worksheet('ip反查域名')
    headings7 = ['ip', '域名']
    worksheet7.set_column('A:A', 12)
    worksheet7.set_column('B:B', 28)
    worksheet7.write_row('A1', headings7)

    worksheet8 = workbook.add_worksheet('备案查询')
    headings8 = ['域名', '主备案号']
    worksheet8.set_column('A:A', 12)
    worksheet8.set_column('B:B', 28)
    worksheet8.write_row('A1', headings8)

    worksheet9 = workbook.add_worksheet('存活网站标题')
    headings9 = ['网址', '状态码', '标题', 'X-Powered-By']
    worksheet9.set_column('A:A', 35)
    worksheet9.set_column('B:B', 8)
    worksheet9.set_column('C:C', 28)
    worksheet9.set_column('D:D', 28)
    worksheet9.write_row('A1', headings9)

    worksheet10 = workbook.add_worksheet('漏洞扫描')
    headings10 = ['漏洞名', 'url', '状态']
    worksheet10.set_column('A:A', 12)
    worksheet10.set_column('B:B', 28)
    worksheet10.set_column('C:C', 28)
    worksheet10.write_row('A1', headings10)
    workbook.close()


'''递归获取父域名'''


def Common_getTopDomainName(Subdomain, FatherUrl):
    temp_url = FatherUrl.split('.', 1)[1]
    if Subdomain == temp_url:
        return temp_url
    else:
        return Common_getTopDomainName(Subdomain, temp_url)


'''功能：简单的判断下当 端口为443,80的时候返回的格式为http?s:// + ....，否则其他端口的话每个url都返回两次'''


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
