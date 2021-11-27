# coding=utf-8

from core.public import *
from spider import BaseSpider


class CtfrSpider(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://crt.sh/?q=%.{}&output=json'
        self.source = 'CtfrSpider'

    def writeFile(self, web_lists, page):
        try:
            workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
            worksheet = workbook.worksheets[page]  # 打开的是证书的sheet
            index = 0
            while index < len(web_lists):
                web = list()
                web.append(web_lists[index]['ssl'])
                web.append(web_lists[index]['subdomain'])
                worksheet.append(web)
                index += 1
            workbook.save(abs_path + str(self.domain) + ".xlsx")
            workbook.close()
        except Exception as e:
            print('[-] [{}] writeFile error, error is {}'.format(self.source, e.__str__()))

    async def spider(self):
        sslInfo = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=self.addr.format(self.domain), verify_ssl=False, headers=self.headers, proxy='http://127.0.0.1:7890') as response:
                    text = await response.json()
                    for (key, value) in enumerate(text):
                        subdomainSSL = value['name_value'].split('\n')
                        if len(subdomainSSL) == 2:
                            domainInfo = {'ssl': subdomainSSL[0], 'subdomain': subdomainSSL[1]}
                            self.resList.append(subdomainSSL[1])
                        else:
                            domainInfo = {'ssl': 'None', 'subdomain': subdomainSSL[0]}
                            self.resList.append(subdomainSSL[0])

                        # 一起放到列表中进行存储
                        sslInfo.append(domainInfo)
        except aiohttp.ClientHttpProxyError:
            print('[-] curl ctfr.sh need outer proxy.')
            return []
        except Exception as e:
            print('[-] curl crt.sh error, the erorr is {}'.format(e.args))
            return []
        
        # 列表中的字典去重
        self.writeFile(getUniqueList(sslInfo), 3)

        # 返回结果
        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))

    async def main(self):
        await self.spider()
        return self.resList


if '__main__' == __name__:
    baidu = CtfrSpider('zjhu.edu.cn')
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(baidu.main())
