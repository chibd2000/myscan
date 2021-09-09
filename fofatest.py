# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-06 21:23

import requests
import json

# with open('json.txt', 'a+', encoding='utf-8'):
#     [
#       {'service': 'redis', 'ip': ['1.1.1.1:6379','2.2.2.2:9874']},
#       {'service': 'rsync', 'ip': ['3.3.3.3:873','4.4.4.4:783']}
#      ]


if __name__ == '__main__':
    res = []
    # fineReport
    # fineReport = 'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=RmluZVJlcG9ydA==&size=1000&&fields=host'
    # resp = requests.get(url=fineReport)

    # ftp
    # ftp = 'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=ImZ0cCIgJiYgdHlwZT0ic2VydmljZSIgJiYgY291bnRyeT0iQ04i&size=10000&&fields=host'
    # resp = requests.get(url=ftp)

    # memcache = 'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=Im1lbWNhY2hlIiAmJiB0eXBlPSJzZXJ2aWNlIiAmJiBjb3VudHJ5PSJDTiI=&size=10000&&fields=host'
    # resp = requests.get(url=memcache)

    # mongodb = 'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=Im1vbmdvZGIiICYmIHR5cGU9InNlcnZpY2UiICYmIGNvdW50cnk9IkNOIg==&size=1000&&fields=host'

    # ldap = 'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=cHJvdG9jb2w9ImxkYXAiICYmIGNvdW50cnk9IkNOIg==&size=1000&&fields=host'

    # mssql = 'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=cHJvdG9jb2w9Im1zc3FsIiAmJiBjb3VudHJ5PSJDTiI=&size=1000&&fields=host'

    # zookeeper = 'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=KCJ6b29rZWVwZXIiKSAmJiAoaXNfaG9uZXlwb3Q9ZmFsc2UgJiYgaXNfZnJhdWQ9ZmFsc2Up&size=1000&&fields=host'

    # ssh = 'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=c3No&size=1000&fields=host'
    mysql = 'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=Im15c3FsIg==&size=300&fields=host'
    resp = requests.get(url=mysql)
    result = json.loads(resp.content.decode('utf-8'))

    # serviceExploit
    ipList = []
    for _ in result.get('results'):
        ipList.append(_)
    res.append({'service': 'mysql', 'ip': ipList})
    print(res)

    # webExploit
    # domainList = []
    # for _ in result.get('results'):
    #     domainList.append(_)
    # print(domainList)
