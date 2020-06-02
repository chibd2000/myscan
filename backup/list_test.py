# coding=utf-8

import re

# 用来格式化数据用的

ip_port = {}

task_list = ['yxapi.ncist.cn', '60.190.19.150:53', '60.12.29.178:80', '60.190.19.116', '60.12.29.162:500', 'travel.ncist.cn', 'dyb.nchs.edu.cn',
 '60.12.29.59', '60.190.19.123', '60.190.19.90', '60.12.29.60:80', '60.190.19.84:110', 'www.hexiehealth.com',
 'info.nbcc.cn', '60.12.29.178', '60.190.19.88:8086', '60.12.29.72', '60.190.19.150:22', '60.12.29.58:8084',
 'webvpn.ncist.cn', '60.12.29.162:443', '60.12.29.73', '60.190.19.26:53', '60.190.19.162:80','60.190.19.162:81']

clear_task_list = []

domain = 'ncist.cn'

for aa in task_list:
    i = aa.split(':')
    if ':' in aa:
        if str(i[0]) in ip_port.keys():
            ip_port[str(i[0])].append(str(i[1]))
        else:
            ip_port[str(i[0])] = [str(i[1])]

for aa in task_list:

    info = dict()
    # 第一种情况：子域名
    if domain in aa:
        info['subdomain'] = aa
        info['ips'] = ''
        info['port'] = None
        info['target'] = 'yes'  # 作为子域名的一个标识符
        clear_task_list.append(info)

    # 第二种情况：非子域名 非正常域名 非ip
    elif domain not in aa and not re.match(r'\d+.\d+.\d+:?\d?', aa):
        info['subdomain'] = aa
        info['ips'] = ''
        info['port'] = None
        info['target'] = 'no'
        clear_task_list.append(info)

    # 第三种情况：非子域名 非正常域名 是ip
    else:
        i = aa.split(':')
        if ':' in aa:
            ip = i[0]
            info['ips'] = ip
            info['port'] = ip_port[ip]
            info['target'] = 'no'
            info['subdomain'] = ''
            clear_task_list.append(info)
        else:
            ip = i[0]
            info['ips'] = ip
            info['port'] = list()
            info['target'] = 'no'
            info['subdomain'] = ''
            clear_task_list.append(info)

print(clear_task_list)

#
# for i in task_list:
#     info = dict()
#
#     # 第一种情况：子域名
#     if domain in i:
#         info['subdomain'] = i
#         info['ips'] = ''
#         info['port'] = None
#         info['target'] = 'yes'  # 作为子域名的一个标识符
#         clear_task_list.append(info)
#
#     # 第二种情况：非子域名 非正常域名 非ip
#     elif domain not in i and not re.match(r'\d+.\d+.\d+:?\d?', i):
#         info['subdomain'] = i
#         info['ips'] = ''
#         info['port'] = None
#         info['target'] = 'no'
#         clear_task_list.append(info)
#
#     # 第三种情况：非子域名 非正常域名 是ip
#     else:
#         # # 循环clear_task_list列表
#         # for j in clear_task_list:  # [{"subdomain": "","ips": "1.1.1.1","port":[7777,8888],"target","yes"}]
#         #     # 如果ip已经在clear_task_list出现
#         temp = i
#         temp_ip = temp
#         if ':' in temp:
#             temp_ip = temp.split(':')[0]
#             temp_port = temp.split(':')[1]
#
#         for j in clear_task_list:
#             if domain in j['subdomain'] and not re.match(r'\d+.\d+.\d+:?\d?', j['subdomain']):
#                 continue
#             print(j)
#
#             if temp_ip == j['ips']:
#                 # 如果当前ip的端口是存在的
#                 if ':' in j['ips']:
#
#                     port = i.split(':')[1]
#                     # 如果该列表中的port列表是空的，那么直接给这个列表再次赋值，结果：[] -> ['7777']
#                     if j['port'] == list():
#                         clear_task_list[clear_task_list.index(j)]['port'] = [str(port)]
#                     else:
#                         # 如果该列表中的port列表不为空，那么在原来的基础上append，结果：['7777'] -> ['7777','8888']
#                         clear_task_list[clear_task_list.index(j)]['port'].append(str(port))
#                 else:
#                     continue
#
#             # 如果ip没有在clear_task_list出现过
#             else:
#                 # 如果当前的ip端口是存在的
#                 if ':' in i:
#                     ip = i.split(':')[0]
#                     port = i.split(':')[1]
#                     info['ips'] = ip
#                     info['port'] = [str(port)]
#                     info['target'] = 'no'
#                     info['subdomain'] = ''
#                     clear_task_list.append(info)
#                     break
#
#                 # 如果当前的ip端口不存在的
#                 else:
#                     ip = i.split(':')[0]
#                     info['ips'] = ip
#                     info['port'] = list()
#                     info['target'] = 'no'
#                     info['subdomain'] = ''
#                     clear_task_list.append(info)
#                     break



