# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-29 3:05

from spider.thirdLib.third import *


def Entrus_Api(domain):
    result = set()
    try:
        url = 'https://ctsearch.entrust.com/api/v1/certificates'
        params = {'fields': 'subjectDN',
                  'domain': domain,
                  'includeExpired': 'true'}
        response = requests.get(url=url,params=params)
        rest = (response.json())
        for c in rest:
            try:
                result.add(c['subjectDN'].split(',')[0].replace('cn=', '').replace('*.', ''))
            except:
                pass
    except Exception as e:
        pass
    print('[+ Entrus API] Entrus接口 : {} 捕获子域名总数 : {}'.format(domain, len(result)))
    return list(result)