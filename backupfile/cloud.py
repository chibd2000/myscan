# coding=utf-8

# 失败脚本 原因：js好像是动态的 8太懂
import requests
import re
import execjs

requests.packages.urllib3.disable_warnings()

#第一次get请求 返回的Set-Cookie 中的__cfduid的值 作为第二次请求中 __cfduid字段的只

'''CouldFlare 5s判断绕过 execjs模块'''
def bypass(domain):
    node = execjs.get()
    resp = requests.get(domain, verify=False)
    # get中 请求的
    _challenage = re.search(r'<form class="challenge-form" id="challenge-form" action="(.*?)" method="POST" enctype="application/x-www-form-urlencoded">', resp.text, re.S).group(1).replace('&amp;', '&')

    # post中 r的字段的值
    _r = re.search(r'name="r" value="(.*?)"/>', resp.text, re.S).group(1)
    _jschl_vc = re.search(r'value="(.*?)" id="jschl-vc" name="jschl_vc"/>', resp.text).group(1)
    _pass = re.search(r'name="pass" value="(.*?)"/>', resp.text, re.S).group(1)

    # pattern = re.compile('setTimeout\(function\(\)\{(.*?)f.action \+= location.hash;', re.S)
    # code = pattern.findall(resp.text)[0]

    code = re.search(r'setTimeout\(function\(\)\{(.*?)f.action \+= location.hash;', resp.text, flags=re.S).group(1)

    # jsdom环境配置
    # code = 'const jsdom = require("jsdom");' \
    #        'const { JSDOM } = jsdom;' \
    #        'const dom = new JSDOM(`<!DOCTYPE html><p>Hello world</p>`);' \
    #        'window = dom.window;' \
    #        'document = window.document;' \
    #        'XMLHttpRequest = window.XMLHttpRequest;' + code

    code = re.sub(r'\s+t = document.*-1\);', 't="dns.bufferover.run"', code, flags=re.S | re.I)
    code = re.sub('a.value', 'value', code)
    code = 'function bypass(){' + code.strip() + ';return value;}'
    print(code)
    bypass = node.compile(code, cwd=r"C:\Users\dell\AppData\Roaming\npm\node_modules")
    t = bypass.call('bypass')
    # print(t)


    headers = {
        'Cookie': resp.headers.get('Set-Cookie')
    }


if __name__ == '__main__':
    bypass('https://dns.bufferover.run/dns?q=nbcc.cn')
