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

    def spider(self):
        sslInfo = []
        try:
            resp = requests.get(self.addr.format(self.domain))
            if resp.status_code != 200:
                print("[-] crt.sh not available!")
                return

            for (key, value) in enumerate(resp.json()):
                subdomainSSL = value['name_value'].split('\n')
                if len(subdomainSSL) == 2:
                    self.resList.append(subdomainSSL[1])
                    domainInfo = {
                        'ssl': subdomainSSL[0],
                        'subdomain': subdomainSSL[1]
                    }
                else:
                    domainInfo = {
                        'ssl': 'None',
                        'subdomain': subdomainSSL[0]
                    }
                # 一起放到列表中进行存储
                sslInfo.append(domainInfo)
        except Exception as e:
            print('[-] curl crt api error. {}'.format(e.args))

        # 列表中的字典去重
        self.writeFile(getUniqueList(sslInfo), 1)

        # 返回结果
        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList

    def main(self):
        logging.info("Ctfr Spider Start")
        return self.spider()


if '__main__' == __name__:
    CtfrSpider('nbcc.cn').main()
