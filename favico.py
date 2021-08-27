# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-27 13:32

# python 3

import mmh3
import requests
import codecs
import hashlib
requests.packages.urllib3.disable_warnings()

resp = requests.get('http://binyue-uat.geely.com:8080/favicon.ico')
favicon = codecs.encode(resp.content, "base64")
hash = mmh3.hash(favicon)
print(hash)
m1 = hashlib.md5()
m1.update(resp.content)
theMD5 = m1.hexdigest()
print(theMD5)

