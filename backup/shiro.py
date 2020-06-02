# coding=utf-8

import requests

# shiro_list = [
#     'http://182.61.19.157:84/loginIn.do',
# ]

headers = {
    'Cookie': 'rememberMe=11;'
}

# for i in shiro_list:
resp = requests.get("http://seat.ncist.edu.cn/", headers=headers, allow_redirects=False) # allow_redirects设置为False 要不然重定向的发包导致检测不到
if 'rememberMe' in str(resp.headers):
    print("特征符合Shiro框架，可以进行检测是否存在shiro反序列化漏洞")

