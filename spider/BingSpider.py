# coding=utf-8

from spider.public import *
from spider import BaseSpider

from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup


class BingSpider(BaseSpider):

    def __init__(self, domain):
        super().__init__()
        self.source = 'BingSpider'  #
        self.domain = domain
        # self.words = ['admin', 'login', 'system', 'register', 'upload', '后台', '系统', '登录']
        self.words = ['登录']
        self.PAGES = 1  # 默认跑5页
        self.webList = []
        self.addr = 'https://www.bing.com/search?q={}&first={}'
        self.headers.update({'Cookie': 'SRCHHPGUSR=ADLT=DEMOTE&NRSLT=50'})

    def writeFile(self, web_lists, page):
        workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(web_lists[index]['spider'])
            web.append(web_lists[index]['keyword'])
            web.append(web_lists[index]['link'])
            web.append(web_lists[index]['title'])
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(self.domain) + ".xlsx")
        workbook.close()

    async def fetch(self, word):  # host 既可以是域名也可以是IP
        for page in range(1, self.PAGES + 1):
            tmp = page - 2
            if tmp == -1:
                first_value = 1
            elif tmp == 0:
                first_value = 2
            else:
                first_value = tmp * 10 + 2
            try:
                async with aiohttp.ClientSession() as session:
                    print(self.addr.format(quote(word + " site:*." + self.domain), first_value))
                    async with session.get(url=self.addr.format(quote(word + " site:*." + self.domain), first_value),
                                           headers=self.headers, verify_ssl=False, timeout=self.reqTimeout) as response:
                        text = await response.text(encoding='utf-8')
                        soup = BeautifulSoup(text, 'html.parser')
                        lis = soup.find_all('li', class_='b_algo')
                        for li in lis:
                            li_a = li.find('a')
                            link = li_a['href']  # 链接
                            title, service, respContent = await self.getTitleAndService(session, link)  # 该函数写在基类中
                            self.resList.extend(self.matchSubdomain(self.domain, respContent))
                            self.resList.append(urlparse(link).netloc)
                            webInfo = {'spider': 'Bing', 'keyword': word, 'link': link, 'title': title}
                            self.webList.append(webInfo)
            except Exception as e:
                print(e.args)
                # pass

                # headers = {
                #     'Host': self.hostname,
                #     'Cookie': 'SRCHHPGUSR=ADLT=DEMOTE&NRSLT=50',
                #     'Accept-Language': 'en-us,en',
                #     'User-agent': Core.get_user_agent()
                # }
                # base_url = f'https://{self.server}/search?q=%40"{self.word}"&count=50&first=xx'
                # urls = [base_url.replace("xx", str(num)) for num in range(0, self.limit, 50) if num <= self.limit]
                # responses = await AsyncFetcher.fetch_all(urls, headers=headers, proxy=self.proxy)
                # for response in responses:
                #     self.total_results += response

    # 爬子域名
    async def spider(self):
        await asyncio.gather(*[asyncio.create_task(self.fetch(word)) for word in self.words])
        self.writeFile(getUniqueList(self.webList), 1)

        # 返回结果
        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))

    async def main(self):
        logging.info("BingSpider Start")
        await self.spider()
        return self.resList


if __name__ == '__main__':
    a = BingSpider('nbcc.cn')
    a.spider()
