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
    resp = requests.get(
        'https://fofa.so/api/v1/search/all?email=496347658@qq.com&key=627c0a4e86e7111baf74c731f8e77f14&qbase64=InJtaSIgJiYgY291bnRyeT0iQ04i&size=1000&&fields=host')
    result = json.loads(resp.content.decode('utf-8'))

    ipList = []
    for _ in result.get('results'):
        ipList.append(_)
    res.append({'service': 'rmi', 'ip': ipList})
    print(res)