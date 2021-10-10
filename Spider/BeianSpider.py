# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 13:46
from spider.public import *
from spider import BaseSpider
import math
from urllib.parse import quote

class BeianSpider(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'Chinaz Beian'
        self.domain = domain
        self.addr1 = 'http://icp.chinaz.com/{}'
        self.addr2 = 'http://icp.chinaz.com/Home/PageData'

    def writeFile(self, web_lists, page):
        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(web_lists[index]['host'])
            web.append(web_lists[index]['webName'])
            web.append(web_lists[index]['owner'])
            web.append(web_lists[index]['permit'])
            web.append(web_lists[index]['typ'])
            web.append(web_lists[index]['verifyTime'])
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(self.domain) + ".xlsx")
        workbook.close()

    # 解析chinaz返回结果的json数据
    # @ske@ske
    def parseJson(self, json_ret):
        results = json_ret['data']
        for result in results:
            self.resList.append(result)
            # companyName = result['webName']
            # newDomain = result['host']
            # time = result['verifyTime']
            # chinazNewDomains.append((companyName, newDomain, time))  #

    async def spider(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr1.format(self.domain), headers=self.headers,
                                       timeout=self.reqTimeout,
                                       verify_ssl=False, allow_redirects=False) as response:
                    if response is not None:
                        # @ske 第一个请求查询公司名称
                        text = await response.text()
                        companyName = re.search("var kw = '([\S]*)'", text)
                        if companyName:
                            companyName = companyName.group(1)
                            print('公司名: {}'.format(companyName))
                            companyNameUrlEncode = quote(str(companyName))
                            # @ske 第二个请求查询该公司的顶级域名
                            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
                            data = 'pageNo=1&pageSize=20&Kw={}'.format(companyNameUrlEncode)
                            try:
                                async with session.post(url=self.addr2.format(self.domain), headers=headers, data=data, timeout=self.reqTimeout, verify_ssl=False, allow_redirects=False) as response2:
                                    if response2 is not None:
                                        text2 = await response2.json()
                                        if 'amount' in text2.keys():
                                            amount = text2.get('amount')
                                            pages = math.ceil(amount / 20)
                                            print('页数: {}'.format(pages))
                                            self.parseJson(text2)
                                            for page in range(2, pages + 1):
                                                print('请求第{}页'.format(page))
                                                data = 'pageNo={}&pageSize=20&Kw={}'.format(page, companyNameUrlEncode)
                                                async with session.post(url=self.addr2.format(self.domain), headers=headers,
                                                                        data=data, timeout=self.reqTimeout,
                                                                        verify_ssl=False,
                                                                        allow_redirects=False) as response3:
                                                    if response2 is not None:
                                                        text3 = await response3.json()
                                                        self.parseJson(text3)
                            except Exception as e:
                                print('[-] curl {} error, {}'.format(self.addr2, e.__str__()))
                        else:
                            print('没有匹配到公司名')
        except Exception as e:
            print('[-] curl BeianSpider error, {}'.format(self.addr1.format(self.domain), e.__str__()))

        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        # 列表中的字典去重/写入文件
        self.writeFile(getUniqueList(self.resList), 0)

    async def main(self):
        await self.spider()


if __name__ == '__main__':
    beian = BeianSpider('zjhu.edu.cn')
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(beian.main())

