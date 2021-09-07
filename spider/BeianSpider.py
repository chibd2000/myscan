# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 13:46
from spider.public import *
from spider import BaseSpider
import math
from urllib.parse import quote
from termcolor import cprint
from lxml import etree


class BeianSpider(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'Beian'
        self.domain = domain
        self.addr = 'https://icp.chinaz.com/home/info?host={}'

    def writeFile(self, web_lists, page):
        pass

    def chinaz(self):
        try:
            response = requests.get(url=self.addr.format(self.domain), headers=self.headers)
            html = etree.HTML(response.text)
            url_href = html.xpath('//div[@class="siteInfo"]/p/text()')
            if not url_href[0].startswith('--'):
                urls = url_href[2:]
                print(urls)
        except Exception as e:
            print(e)

    # 解析chinaz返回结果的json数据
    def parse_json(self, json_ret):
        chinazNewDomains = []
        results = json_ret['data']
        for result in results:
            companyName = result['webName']
            newDomain = result['host']
            time = result['verifyTime']
            chinazNewDomains.append((companyName, newDomain, time))  #
        chinazNewDomains = list(set(chinazNewDomains))
        return chinazNewDomains

    def spider(self):

        cprint('Load chinazApi: ', 'green')

        chinazNewDomains = []
        tempDict = {}
        tempList = []

        # 获取域名的公司名字
        url = r'http://icp.chinaz.com/{}'.format(self.domain)
        try:
            res = requests.get(url=url, headers=self.headers, allow_redirects=False, verify=False)
        except Exception as e:
            print('[error] request : {}\n{}'.format(url, e.args))
            return []
        text = res.text

        companyName = re.search("var kw = '([\S]*)'", text)
        if companyName:
            companyName = companyName.group(1)
            print('公司名: {}'.format(companyName))
            companyNameUrlEncode = quote(str(companyName))
        else:
            print('没有匹配到公司名')
            return []

        # 备案反查域名
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        url = 'http://icp.chinaz.com/Home/PageData'
        data = 'pageNo=1&pageSize=20&Kw=' + companyNameUrlEncode
        try:
            res = requests.post(url=url, headers=headers, data=data, allow_redirects=False, verify=False)
        except Exception as e:
            print('[error] request : {}\n{}'.format(url, e.args))
            return []

        json_ret = json.loads(res.text)
        # print(json_ret)
        if 'amount' not in json_ret.keys():
            return chinazNewDomains
        amount = json_ret['amount']
        pages = math.ceil(amount / 20)
        print('页数: {}'.format(pages))
        # 解析返回的json数据包，过滤出公司名，域名，时间
        tempList.extend(self.parse_json(json_ret))
        # for _ in chinazNewDomains:
        #     print(_)

        # 继续获取后面页数
        for page in range(2, pages + 1):
            print('请求第{}页'.format(page))
            data = 'pageNo={}&pageSize=20&Kw='.format(page) + companyNameUrlEncode
            try:
                res = requests.post(url=url, headers=headers, data=data, allow_redirects=False, verify=False)
                json_ret = json.loads(res.text)
                tempList.extend(self.parse_json(json_ret))
            except Exception as e:
                print('[error] request : {}\n{}'.format(url, e.args))

        for each in tempList:
            if each[1] not in tempDict:
                tempDict[each[1]] = each
                chinazNewDomains.append(each)

        print('chinazApi去重后共计{}个顶级域名'.format(len(chinazNewDomains)))
        # for _ in chinazNewDomains:
        #     print(_)
        return chinazNewDomains


if __name__ == '__main__':
    BeianSpider("zjhu.edu.cn")
