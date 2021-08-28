# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-28 11:26

import requests
from lxml import etree
from urllib.parse import quote, urlparse

header = {
    'Cookie': 'BIDUPSID=QE32B6F0AQ4316C55C645EBF1361E641'
}

resp = requests.get(url='http://www.baidu.com/s?wd=%E5%90%8E%E5%8F%B0%20site%3A%2A.baidu.com&pn=00', headers=header)
text = resp.content.decode('utf-8')
print(text)
selector = etree.HTML(text)
resList = []
for i in range(9):
    linkList = selector.xpath('//*[@id="' + str(i+1) + '"]/h3/a/@href') # //*[@id="1"]/h3/a/@href
    print(linkList)
    if linkList == []:
        break
    for _ in linkList:
        resList.append(_)
print(resList)