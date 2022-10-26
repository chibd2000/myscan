# coding=utf-8

from string import digits
from core.constant import PORT_RULES
import xlsxwriter
import hashlib
import random
import yaml


def save_dict_to_yaml(dict_value: dict, save_path: str):
    """dict保存为yaml"""
    with open(save_path, 'w') as file:
        file.write(yaml.dump(dict_value, allow_unicode=True))


def read_yaml_to_dict(yaml_path: str):
    try:
        with open(yaml_path, 'rb') as file:
            config_dict = yaml.load(file.read(), Loader=yaml.FullLoader)
            return config_dict
    except Exception as e:
        exit(print("[-] read_yaml_to_dict error, the error is {}".format(e.args)))


def get_url(domain):
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


# 根据port识别服务
def get_port_service(port):
    for k, v in PORT_RULES.items():
        for b in v:
            if int(b) == int(port):
                return k
    return 'Unknown'


def random_md5(length=16, ret_plain=False):
    plain = ''.join([random.choice(digits) for _ in range(length)])
    m = hashlib.md5()
    m.update(bytes(plain, 'utf-8'))
    cipher = m.hexdigest() if hex else m.hexdigest()
    if ret_plain:
        return [plain, cipher]
    else:
        return cipher


# 创建图表
def create_xlsx(target):
    workbook = xlsxwriter.Workbook(target + ".xlsx")
    worksheet1 = workbook.add_worksheet('备案')
    headings1 = ['域名', '网站', 'ICP备案', '备案时间']
    worksheet1.set_column('A:A', 18)
    worksheet1.set_column('B:B', 29)
    worksheet1.set_column('C:C', 22)
    worksheet1.set_column('D:D', 20)
    worksheet1.write_row('A1', headings1)

    worksheet2 = workbook.add_worksheet('企业架构')
    headings2 = ['类型', '公司名称', 'Information', '邮箱', '联系电话', '域名', '备案']  # 'APP', '微信公众号'
    worksheet2.set_column('A:A', 10)
    worksheet2.set_column('B:B', 35)
    worksheet2.set_column('C:C', 25)
    worksheet2.set_column('D:D', 15)
    worksheet2.set_column('E:E', 14)
    worksheet2.set_column('F:F', 24)
    worksheet2.set_column('G:G', 15)
    worksheet2.set_column('H:H', 30)
    worksheet2.set_column('I:I', 30)
    worksheet2.write_row('A1', headings2)

    worksheet3 = workbook.add_worksheet('爬虫')
    headings3 = ['爬虫', '关键字', '链接', '标题']  # 设置表头
    worksheet3.set_column('A:A', 7)
    worksheet3.set_column('B:B', 20)
    worksheet3.set_column('C:C', 66)
    worksheet3.set_column('D:D', 60)
    worksheet3.write_row('A1', headings3)

    worksheet4 = workbook.add_worksheet('证书SSL')
    headings4 = ['证书信任域名', '域名']
    worksheet4.set_column('A:A', 24)
    worksheet4.set_column('B:B', 24)
    worksheet4.write_row('A1', headings4)

    worksheet5 = workbook.add_worksheet('子域名A记录')
    headings5 = ['子域名', 'A记录IP']
    worksheet5.set_column('A:A', 40)
    worksheet5.set_column('B:B', 23)
    worksheet5.write_row('A1', headings5)

    worksheet6 = workbook.add_worksheet('IP存活段')
    headings6 = ['IP段分布', '存在IP', '数量']
    worksheet6.set_column('A:A', 19)
    worksheet6.set_column('B:B', 90)
    worksheet6.set_column('C:C', 10)
    worksheet6.write_row('A1', headings6)

    worksheet7 = workbook.add_worksheet('ASN')
    headings7 = ['ASN分布']
    worksheet7.set_column('A:A', 8)
    worksheet7.write_row('A1', headings7)

    worksheet8 = workbook.add_worksheet('ip反查子域名')
    headings8 = ['ip', '域名']
    worksheet8.set_column('A:A', 20)
    worksheet8.set_column('B:B', 30)
    worksheet8.write_row('A1', headings8)

    worksheet10 = workbook.add_worksheet('Fofa')
    headings10 = ['空间引擎名', 'HOST', '标题', 'ip', '根域名', '服务', '协议', 'asn', '查询语句']
    worksheet10.set_column('A:A', 12)
    worksheet10.set_column('B:B', 28)
    worksheet10.set_column('C:C', 37)
    worksheet10.set_column('D:D', 22)
    worksheet10.set_column('E:E', 20)
    worksheet10.set_column('F:F', 25)
    worksheet10.set_column('G:G', 8)
    worksheet10.set_column('H:H', 8)
    worksheet10.set_column('I:I', 25)
    worksheet10.write_row('A1', headings10)

    worksheet11 = workbook.add_worksheet('Hunter')
    headings11 = ['空间引擎名', 'HOST', '标题', 'ip', '根域名', '服务', '协议', 'asn', '查询语句']
    worksheet11.set_column('A:A', 12)
    worksheet11.set_column('B:B', 28)
    worksheet11.set_column('C:C', 37)
    worksheet11.set_column('D:D', 22)
    worksheet11.set_column('E:E', 20)
    worksheet11.set_column('F:F', 25)
    worksheet11.set_column('G:G', 8)
    worksheet11.set_column('H:H', 8)
    worksheet11.set_column('I:I', 25)
    worksheet11.write_row('A1', headings11)

    worksheet12 = workbook.add_worksheet('Quake')
    headings12 = ['空间引擎名', 'HOST', '标题', 'ip', '根域名', '服务', '协议', 'asn', '查询语句']
    worksheet12.set_column('A:A', 12)
    worksheet12.set_column('B:B', 28)
    worksheet12.set_column('C:C', 37)
    worksheet12.set_column('D:D', 22)
    worksheet12.set_column('E:E', 20)
    worksheet12.set_column('F:F', 25)
    worksheet12.set_column('G:G', 8)
    worksheet12.set_column('H:H', 8)
    worksheet12.set_column('I:I', 25)
    worksheet12.write_row('A1', headings12)

    worksheet13 = workbook.add_worksheet('Shodan')
    headings13 = ['空间引擎名', 'HOST', '标题', 'ip', '根域名', '服务', '协议', 'asn', '查询语句']
    worksheet13.set_column('A:A', 12)
    worksheet13.set_column('B:B', 28)
    worksheet13.set_column('C:C', 37)
    worksheet13.set_column('D:D', 22)
    worksheet13.set_column('E:E', 20)
    worksheet13.set_column('F:F', 25)
    worksheet13.set_column('G:G', 8)
    worksheet13.set_column('H:H', 8)
    worksheet13.set_column('I:I', 25)
    worksheet13.write_row('A1', headings13)

    worksheet14 = workbook.add_worksheet('端口扫描')
    headings14 = ['ip', '端口', '服务', '标题', '服务版本信息']
    worksheet14.set_column('A:A', 20)
    worksheet14.set_column('B:B', 10)
    worksheet14.set_column('C:C', 21)
    worksheet14.set_column('D:D', 30)
    worksheet14.set_column('E:E', 150)
    worksheet14.write_row('A1', headings14)

    worksheet15 = workbook.add_worksheet('存活网站标题')
    headings15 = ['网址', '状态码', '标题', 'X-Powered-By']
    worksheet15.set_column('A:A', 51)
    worksheet15.set_column('B:B', 7)
    worksheet15.set_column('C:C', 50)
    worksheet15.set_column('D:D', 28)
    worksheet15.write_row('A1', headings15)

    worksheet16 = workbook.add_worksheet('漏洞扫描')
    headings16 = ['漏洞名', 'url', '组件']
    worksheet16.set_column('A:A', 30)
    worksheet16.set_column('B:B', 50)
    worksheet16.set_column('C:C', 28)
    worksheet16.write_row('A1', headings16)

    worksheet17 = workbook.add_worksheet('FUZZ')
    headings17 = ['地址']
    worksheet17.set_column('A:A', 100)
    worksheet17.write_row('A1', headings17)

    workbook.close()


# 递归获取父域名
def get_top_domain_name(subdomain, fa_url):
    temp_url = fa_url.split('.', 1)[1]
    if subdomain == temp_url:
        return temp_url
    else:
        return get_top_domain_name(subdomain, temp_url)


# 简单的判断下当 端口为443,80的时候返回的格式为http?s:// + ....，否则其他端口的话每个url都返回两次
def get_url_by_port(domain, port):
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
