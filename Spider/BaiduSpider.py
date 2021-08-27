# coding=utf-8

from spider.BaseSpider import *

from urllib.parse import quote, urlparse
# 一个搜索引擎爬取的过程：
# 1、爬取链接
# 2、对链接进行访问重定向到真正的网址
# 3、对重定向过后的网站进行保存写入到文件中

# 关于百度的人机验证绕过方法：加上cookie头
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

abs_path = os.getcwd() + os.path.sep


class BaiduSpider(Spider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'BaiduSpider'  #
        self.domain = domain
        self.webList = []

    # 保存文件
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

    # 爬取链接
    def keyword(self, kw, page=1):
        kw = quote(kw)
        url = 'https://www.baidu.com/s?wd=%s&pn=%s0' % (kw, page)
        req = requests.get(url, headers=self.headers)
        res = re.findall(r'<a target="_blank" href="(\S+)" class="c-showurl', req.content.decode('utf-8'))
        return list(set(res))

    # 重定向验证
    def location(self, link):
        resp = requests.get(link, allow_redirects=False)
        location = resp.headers.get('Location')
        self.resList.extend(self.matchSubdomain(self.domain, resp.text))
        return location

    async def fetch(self, word):
        for page in range(5):
            results = list(map(self.location, self.keyword(word + " site:*." + self.domain, page)))
            for link in results:
                title, service, respContent = await self.getTitleAndService(link)  # 该函数写在基类中
                self.resList.extend(self.matchSubdomain(self.domain, respContent))
                self.resList.append(urlparse(link).netloc)
                webInfo = {'spider': '百度', 'keyword': word, 'link': link, 'title': title}
                self.webList.append(webInfo)

    # 爬取
    async def spider(self):
        words = ['inurl:system', 'inurl:register', 'inurl:login', 'inurl:admin', 'inurl:manage', 'inurl:upload',
                 '后台', '登陆', '系统', 'upload',
                 'intitle:"Outlook Web App"', 'intitle:"mail"']
        taskList = []
        for word in words:
            taskList.append(asyncio.create_task(self.fetch(word)))
        await asyncio.gather(*taskList)
        print(self.resList)
        self.writeFile(getUniqueList(self.webList), 0)

    # 主函数
    async def main(self):
        logging.info("BaiduSpider Start")
        await self.spider()
        self.resList = list(set(self.resList))
        print(self.resList)
        return self.resList


if __name__ == '__main__':
    baidu = BaiduSpider('4399.com')
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(baidu.main())
