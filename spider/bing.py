# coding=utf-8
from core.data import gLogger
from spider import BaseSpider
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup
import aiohttp
import asyncio


class BingSpider(BaseSpider):

    def __init__(self, domain, name):
        super().__init__()
        self.name = name
        self.source = 'BingSpider'  # module name
        self.domain = domain
        self.words = ['后台', '系统', '登录', 'admin', 'login', 'system', 'register', 'upload']
        # self.words = ['登录']
        self.PAGES = 1  # 默认跑5页
        self.web_list = []
        self.addr = 'https://www.bing.com/search?q={}&first={}'
        self.headers.update({'Cookie': 'SRCHHPGUSR=ADLT=DEMOTE&NRSLT=50'})

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
                    async with session.get(url=self.addr.format(quote(word + " site:*." + self.domain), first_value), headers=self.headers, verify_ssl=False, timeout=self.reqTimeout) as response:
                        text = await response.text(encoding='utf-8')
                        soup = BeautifulSoup(text, 'html.parser')
                        lis = soup.find_all('li', class_='b_algo')
                        for li in lis:
                            li_a = li.find('a')
                            link = li_a['href']  # 链接
                            title, service, resp_content = await self.get_title_and_service(session, link)  # 该函数写在基类中
                            self.res_list.extend(self.match_subdomain(self.domain, resp_content))
                            self.res_list.append(urlparse(link).netloc)
                            web_info = {'spider': 'Bing', 'keyword': word, 'link': link, 'title': title}
                            self.web_list.append(web_info)
            except Exception as e:
                gLogger.myscan_error('curl www.bing.com error, the error is {}'.format(e.args))

    async def spider(self):
        await asyncio.gather(*[asyncio.create_task(self.fetch(word)) for word in self.words])
        self._is_continue = False
        self.write_file(self.get_unique_list(self.web_list), 2)
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))

    async def main(self):
        await self.spider()
        return self.res_list


if __name__ == '__main__':
    a = BingSpider('zjhu.edu.cn')
    a.spider()
