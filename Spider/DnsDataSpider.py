# coding=utf-8

from Spider.BaseSpider import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import json


# 自己写js没成功，这里用了selenium 所以需要配合google浏览器的驱动了
class DnsDataSpider(Spider):
    def __init__(self, target):
        super().__init__()
        self.source = 'Dns Data spider'
        self.target = target
        self.dnsdatalist = list()

    # 写文件
    def write_file(self, web_lists, target, page):
        workbook = openpyxl.load_workbook(abs_path + str(target) + ".xlsx")
        worksheet = workbook.worksheets[page]  # 打开的是证书的sheet
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(web_lists[index]['ssl'])
            web.append(web_lists[index]['submain'])
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(target) + ".xlsx")
        workbook.close()

    # 解析数据，这里用(递归)的方式进行查询
    def get_json_data(self, browser):
        WebDriverWait(browser, 20, 0.5).until(EC.presence_of_element_located((By.TAG_NAME, "pre")))
        json_data = json.loads(browser.find_element_by_tag_name('pre').text)
        if json_data:
            return json_data
        else:
            self.get_json_data(browser)

    # 爬取
    def spider(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--headless')
        browser = webdriver.Chrome(options=options)
        browser.get('https://dns.bufferover.run/dns?q=.' + self.target)
        browser.implicitly_wait(60)

        # json_data = {"FDNS_A": "", "RDNS": ""}

        json_data = self.get_json_data(browser)

        browser.quit()

        try:
            for i in json_data['FDNS_A']:
                if i == '':
                    continue
                else:
                    self.dnsdatalist.extend(i.split(','))
        except:
            pass

        try:
            for j in json_data['RNDS']:
                if j == '':
                    continue
                else:
                    self.dnsdatalist.extend(j.split(','))
        except:
            pass

    def main(self):
        logging.info("DnsDabs_pathataSpider Start")
        self.spider()
        # self.write_file(self.dnsdatalist, self.target, 2)
        return self.dnsdatalist


if __name__ == '__main__':
    DnsDataSpider('nbcc.cn').main()
