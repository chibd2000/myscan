# coding=utf-8

from spider.public import *
from spider import BaseSpider
from urllib.parse import quote, urlparse
from lxml import etree
# 一个搜索引擎爬取的过程：
# 1、爬取链接
# 2、对链接进行访问重定向到真正的网址
# 3、对重定向过后的网站进行保存写入到文件中

# 关于百度的人机验证绕过方法：加上cookie头
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

abs_path = os.getcwd() + os.path.sep


class BaiduSpider(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'BaiduSpider'  #
        self.domain = domain
        self.addr = 'https://www.baidu.com/s?wd={}&pn={}0'
        self.page = 5
        self.webList = []
        self.headers.update({'Cookie': 'BIDUPSID=XE37B6F0AQ4316C55C645EBF1361E642'})
        # self.words = ['inurl:system', 'inurl:register', 'inurl:login', 'inurl:admin', 'inurl:manage', 'inurl:upload',
        #               '后台', '登陆', '系统', 'upload', 'intitle:"mail"']

        self.words = ['inurl:login']

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
    async def keyword(self, session, kw, page=1):
        try:
            async with session.get(url=self.addr.format(quote(kw), page), headers=self.headers, verify_ssl=False, timeout=10) as response:
                await asyncio.sleep(2)
                text = await response.text(encoding='utf-8')
                selector = etree.HTML(text)
                # print(text)
                resList = []
                for i in range(9):
                    linkList = selector.xpath('//*[@id="' + str(i+1) + '"]/h3/a/@href')
                    # print(linkList)
                    for _ in linkList:
                        resList.append(_)
                # print(self.addr.format(quote(kw),page))
                # print(text)
                # res = re.findall(r'<a target="_blank" href="(.*)" class="c-showurl', text)
                # res = re.findall(r'<a class="" href="(.*)" data-showurl-highlight', text)
                return list(set(resList))
        except Exception as e:
            print(e.args)
            return

    # 重定向验证
    async def location(self, session, link):
        try:
            async with session.get(link) as response:
                return response.headers.get('location')
        except Exception as e:
            print(e.args)
            return

    async def fetch(self, word):
        for page in range(self.page):
            try:
                async with aiohttp.ClientSession() as session:
                    redirectlinkList = await self.keyword(session, word + " site:*." + self.domain, page)
                    # print(redirectlinkList)
                    for _ in redirectlinkList:
                        link = await self.location(session, _)
                        # print(link)
                        title, service, respContent = await self.getTitleAndService(session, link)  # 该函数写在基类中
                        # print(title, service)
                        self.resList.extend(self.matchSubdomain(self.domain, respContent))
                        self.resList.append(urlparse(link).netloc)
                        webInfo = {'spider': '百度', 'keyword': word, 'link': link, 'title': title}
                        self.webList.append(webInfo)
            except Exception as e:
                print(e.args)
                return

    # 爬取
    async def spider(self):
        await asyncio.gather(*[asyncio.create_task(self.fetch(word)) for word in self.words])
        # 返回结果
        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        # 列表中的字典去重/写入文件
        self.writeFile(getUniqueList(self.webList), 1)
        return self.resList

    # 主函数
    async def main(self):
        return await self.spider()


if __name__ == '__main__':
    baidu = BaiduSpider('geely.com')
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(baidu.main())
