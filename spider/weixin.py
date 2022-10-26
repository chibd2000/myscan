# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 21:15

import requests
import json
import time
import re
from urllib.parse import quote

"""
POST /wxa-cgi/innersearch/subsearch HTTP/1.1
Host: mp.weixin.qq.com
Connection: close
Content-Length: 787
Accept: application/json, text/plain, */*
Origin: weixin://resourceid
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63030532)
Content-Type: application/x-www-form-urlencoded
Sec-Fetch-Site: cross-site
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7

query=%E5%90%89%E5%88%A9&offset_buf=&from_h5=0&begid=0&longitude=0&latitude=0&h5version=65900700&subsys_type=1&sub_type=1&q_highlight=&search_id=9ae16abe-d2a4-1b4b-63a2-8910cbe4823c&source=0&scene=70&search_scene=1&session_id=10aee92e-4228-e2c8-e29a-d0e6849b96df&ext_buf=&business_type=105&cookie=vUJQGmcanmG3FC3QPeo4LEJryNe%252BlW63j5Hu1QztPpynl9NYpMatBxfs2SUjnm6DBbUW8jt775TkgxL2LwGjgg%253D%253D%257C%257C%257C32001f9c67128bb298ae8532034a55295817565d12471f1fb31a605f1288177be20115d4fb76505206597eb63c942837d444de4bda813c5e5f9e59ca552f302169d65db8a13ff8f6dd45fd2059cf7a42d80ddd79873fa0f3d794fb007a0f2ce0632a2e745b031e57a0724da790fa67736df2d1112a692ae5a04c5683fe791eaf&client_version=1660944639&device=15&sugtype=3&sugid=13315122742475828618&sugpos=0&prefixsug=%E5%90%89%E5%88%A9&sugbuf=
"""


def getApps(query, cookie, session, appIdList, appNameList):
    url = "https://mp.weixin.qq.com/wxa-cgi/innersearch/subsearch"
    params = 'query={query}&cookie={cookie}&begid=0&subsys_type=1&session_id={session}&'.format(query=quote(query), cookie=cookie, session=session)
    buf = 'offset_buf={"page_param":[{"subsys_type":1,"server_offset":0,"server_limit":150,"index_step":150,"index_offset":0}],"client_offset":0,"client_limit":150}'
    params += buf
    response = requests.post(url=url, params=params, verify=False, timeout=10)
    text = response.text
    # print(text)
    appJson = json.loads(text)
    appItems = appJson['respBody']['items']
    for App_Item in appItems:
        App_Item_Json = json.loads(json.dumps(App_Item))
        App_Id = App_Item_Json['appid']
        App_Name = App_Item_Json['nickName']
        appIdList.append(App_Id)
        appNameList.append(App_Name)


def getAssets(X_APP_ID, X_WECHAT_KEY, X_WECHAT_UIN):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/7.0.11(0x17000b21) NetType/WIFI Language/fr",
        "X-WECHAT-KEY": X_WECHAT_KEY,
        "X-WECHAT-UIN": X_WECHAT_UIN  # 微信两个校验值
    }
    url = "https://mp.weixin.qq.com/wxawap/waverifyinfo"
    params = "action=get&appid=" + X_APP_ID
    response = requests.get(url=url, params=params, headers=headers, verify=False, timeout=10)
    text = response.text
    reg = re.search(r"item: (\[[\s\S]*\])", text, re.S | re.I).group(1)
    return eval(reg)


def getMiddleStr(content, startStr, endStr):
    # 获取中间字符串的
    startIndex = content.index(startStr)
    if startIndex >= 0:
        startIndex += len(startStr)
        endIndex = content.index(endStr)
        return content[startIndex:endIndex]


def getWxProgram():
    query = input("请输入要搜的微信的程序名称: ")
    session = "sid_-1194798698_1634124457736"  # 需要自己手动抓一次包
    cookie = "BnogoqzIX2G5zcc8MmvoaHmAe3SBsGTpT1FgI2mIAumf6vGF8Ns1qrCwOjQ18XX5Tu2GWpzsFMf5S2EaIIP38g%253D%253D%257C%257C%257C3c4e414deba83f832c8b21bd2f8e1c7c103fae0a635df0d29796cff53bfeaa72e46029afa428f0633afc49b0b49890c77130e31260e1fee9cd7e50d1802d4afbd41c22cc916d306ce3a06e4f4520100753ac08cb1ca7964873b7d093b9289e44e3b9e1f6180bf3bc16fe4fb3680f088c0c13ff64c4ba02ee585c77968952e6ca"  # 需要自己手动抓一次包
    appIdList = []
    appNameList = []

    # 获取搜索关键字的所有微信小程序的程序名字和对应的id
    try:
        getApps(query, cookie, session, appIdList, appNameList)
        print("返回的程序名: " + ",".join(appNameList))
        print("返回的程序ID: " + ",".join(appIdList))
    except Exception as e:
        print("[-] 小程序列表获取失败，error is {}".format(e.args))
        exit(0)

    # 获取上面微信小程序中要指定获取的小程序id中的 "服务及数据由一下网站提供" 的内容
    appIds = input("请输入对应程序ID(逗号分隔): ")
    # 需要自己手动抓一次包
    wechatKey = "c50ab086d2f93cc4b1737725647e7b6d35c8a67518488c7b11b170059b81a4e091a5c0e35a327b3400d15b2d24df54e8ff9fb1f7aa085f41e907b91770c67cc23068df486ee9cb756462b1722bd0026a69635e5e30802a3d9aab76a26609357f408585637fb12c269fb70b7853938449c0386d3aee3cf51605454b28c0f95097"
    # 需要自己手动抓一次包
    wechatUin = "MzEwMDE2ODU5OA%3D%3D"
    appIdList = appIds.split(",")
    domainList = []  # 存储收集到的相关资产

    for appId in appIdList:
        try:
            appIdDomain = getAssets(appId, wechatKey, wechatUin)
            domainList.extend(appIdDomain)
            print('[+] [{}] [{}] {}'.format(appId, len(appIdDomain), appIdDomain))
        except Exception as e:
            print(appId + "对应的微信小程序域名资产获取失败!")
        time.sleep(10)  # 防访问频繁
    domainList = list(set(domainList))
    print('[+] [{}] {}'.format(len(domainList), domainList))


if __name__ == '__main__':
    getWxProgram()
