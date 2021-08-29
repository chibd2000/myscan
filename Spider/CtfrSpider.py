# coding=utf-8

from spider.BaseSpider import *


class CtfrSpider(Spider):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain
        self.addr = 'https://crt.sh/?q=%.{}&output=json'
        self.source = 'ctfr'

    def writeFile(self, web_lists, page):
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

    async def spider(self):
        sslInfo = []
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                result = await AsyncFetcher.fetch(session=session, url=self.addr.format(self.domain), json=True)
                for (key, value) in enumerate(result):
                    subdomainSSL = value['name_value'].split('\n')
                    if len(subdomainSSL) == 2:
                        domainInfo = {'ssl': subdomainSSL[0], 'subdomain': subdomainSSL[1]}
                        self.resList.append(subdomainSSL[1])
                    else:
                        domainInfo = {'ssl': 'None', 'subdomain': subdomainSSL[0]}
                        self.resList.append(subdomainSSL[0])

                    # 一起放到列表中进行存储
                    sslInfo.append(domainInfo)
        except Exception as e:
            print('[-] curl crt.sh error. {}'.format(e.args))

        # 列表中的字典去重
        self.writeFile(getUniqueList(sslInfo), 1)

        # 返回结果
        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))

    async def main(self):
        logging.info("Ctfr Spider Start")
        await self.spider()
        return self.resList


if '__main__' == __name__:
    CtfrSpider('nbcc.cn').main()
