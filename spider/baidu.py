# coding=utf-8
from core.data import gLogger
from spider import BaseSpider
from urllib.parse import quote, urlparse
from lxml import etree
import aiohttp
import asyncio


class BaiduSpider(BaseSpider):
    def __init__(self, domain, name):
        super().__init__()
        self.name = name
        self.source = 'BaiduSpider'
        self.domain = domain
        self.addr = 'https://www.baidu.com/s?wd={}&pn={}0'
        self.page = 5
        self.web_list = []
        self.headers.update({'Cookie': 'BIDUPSID=XE37B6F0AQ4316C55C645EBF1361E642'})
        self.words = ['inurl:system', 'inurl:register', 'inurl:login', 'inurl:admin', 'inurl:manage', 'inurl:upload']

    # 爬取链接
    async def keyword(self, session, kw, page=1):
        try:
            async with session.get(url=self.addr.format(quote(kw), page), headers=self.headers, verify_ssl=False, timeout=self.reqTimeout) as response:
                await asyncio.sleep(2)
                text = await response.text(encoding='utf-8')
                selector = etree.HTML(text)
                res_list = []
                for i in range(9):
                    link_list = selector.xpath('//*[@id="' + str(i+1) + '"]/h3/a/@href')
                    for _ in link_list:
                        res_list.append(_)
                return list(set(res_list))
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
                    redirect_link_list = await self.keyword(session, word + " site:*." + self.domain, page)
                    for _ in redirect_link_list:
                        link = await self.location(session, _)
                        title, service, resp_content = await self.get_title_and_service(session, link)  # 该函数写在基类中
                        self.res_list.extend(self.match_subdomain(self.domain, resp_content))
                        self.res_list.append(str(urlparse(link).netloc))
                        web_info = {'spider': 'Baidu', 'keyword': word, 'link': link, 'title': title}
                        self.web_list.append(web_info)
            except Exception as e:
                print(e.args)
                return

    # 爬取
    async def spider(self):
        await asyncio.gather(*[asyncio.create_task(self.fetch(word)) for word in self.words])
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        self.write_file(self.get_unique_list(self.web_list), 2)
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))

    # 主函数
    async def main(self):
        await self.spider()
        return self.res_list


if __name__ == '__main__':
    pass
