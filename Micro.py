# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 21:15
# @poc sir

import requests
import json


def getApps(query, number, cookie):
    url = "https://mp.weixin.qq.com/wxa-cgi/innersearch/subsearch"
    params = "query=" + query + "&cookie=" + cookie + '&subsys_type=1&offset_buf= {"page_param":[{"subsys_type":1,"server_offset":0,"server_limit":' + str(
        int(number) + 30) + ',"index_step":' + number + ',"index_offset":0}],"client_offset":0,"client_limit":' + number + '}'
    response = requests.post(url=url, params=params).text
    Apps_Json = json.loads(response)
    App_Items = Apps_Json['respBody']['items']
    for App_Item in App_Items:
        App_Item_Json = json.loads(json.dumps(App_Item))
        App_Id = App_Item_Json['appid']
        App_Name = App_Item_Json['nickName']
        App_Id_List.append(App_Id)
        App_Name_List.append(App_Name)


if __name__ == '__main__':
    query = input("请输⼊要搜的微信⼩程序名称: ")
    number = input("请指定要返回的⼩程序的数量: ")
    cookie = input("请输⼊你获取到的Cookie信息: ")
    App_Id_List = []
    App_Name_List = []
    try:
        getApps(query, number, cookie)
        print("返回的⼩程序名: " + ",".join(App_Name_List))
        print("返回的⼩程序ID: " + ",".join(App_Id_List))
    except:
        print("信息获取失败，请检查！")
