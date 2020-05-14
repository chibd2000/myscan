from Spider.Common.common import *
import json

web_lists = [[{'spider': 'fofa', 'subdomain': '123.123.123.124:22', 'title': '', 'ip': '123.123.123.124', 'domain': '', 'port': '22', 'web_service': '', 'port_service': 'SSH', 'search_keyword': 'ip="123.123.123.123/24" && port="22"'}, {'spider': 'fofa', 'subdomain': '123.123.123.123:22', 'title': '', 'ip': '123.123.123.123', 'domain': '', 'port': '22', 'web_service': '', 'port_service': 'SSH', 'search_keyword': 'ip="123.123.123.123/24" && port="22"'}],[{'spider': 'fofa', 'subdomain': 'https://www.5890788.com', 'title': '', 'ip': '123.123.123.123', 'domain': '5890788.com', 'port': '443', 'web_service': '', 'port_service': 'HTTPS', 'search_keyword': 'ip="123.123.123.123/24" && port="443"'}]]

index = 0
while index < len(web_lists):
    for i in web_lists[index]:
        print(eval(i))

        web = list()
        web.append(i['spider'])
        web.append(i['subdomain'])
        web.append(i['title'])
        web.append(i['ip'])
        web.append(i['domain'])
        web.append(i['port'])
        web.append(i['web_service'])
        web.append(i['port_service'])
        web.append(i['search_keyword'])
        print(web)


    index += 1


