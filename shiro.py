# coding=utf-8

import requests

shiro_list = [
    'http://182.61.19.157:84/loginIn.do',
]

headers = {
    'Cookie': 'rememberMe=11;'
}

for i in shiro_list:
    resp = requests.get("http://www.tyyz.com.cn/", headers=headers)
    if 'rememberMe' in str(resp.headers):
        print(i + " 特征符合Shiro框架，可以进行检测是否存在shiro反序列化漏洞")

