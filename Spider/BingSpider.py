# coding=utf-8

from spider.BaseSpider import *
from urllib.parse import quote, urlparse
import threading
from bs4 import BeautifulSoup


class BingSpider(Spider):
    def writeFile(self, web_lists, page):
        pass

    def spider(self):
        pass

    def main(self):
        pass

    def __init__(self, domain):
        super().__init__()
        self.source = 'BingSpider'  #
        self.domain = domain
        # site:domain inurl:admin inurl:login inurl:system 后台 系统
        self.wds = ['admin', 'login', 'system', 'register', 'upload', '后台', '系统', '登录']
        self.PAGES = 5  # 默认跑5页
        self.TIMEOUT = 10
        self.links = []

    def get_subdomain(self, host, each_wd, i):  # host 既可以是域名也可以是IP
        for page in range(1, self.PAGES + 1):
            q = 'site:{} {}'.format(host, each_wd)
            print('[{}] -> [page: {}]'.format(q, page))
            tmp = page - 2
            if tmp == -1:
                first_value = 1
            elif tmp == 0:
                first_value = 2
            else:
                first_value = tmp * 10 + 2
            url = r'https://www.bing.com/search?q={}&first={}'.format(quote(q), first_value)
            print(url)
            try:
                res = requests.get(url=url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                lis = soup.find_all('li', class_='b_algo')
                for li in lis:
                    li_a = li.find('a')
                    link = li_a['href']  # 链接
                    title = li_a.get_text()  # 标题
                    subdomain = urlparse(link).netloc  # 子域名
                    print('[{}] [page: {}]: {} {} {}'.format(q, page, link, title, subdomain))
                    self.resList.append(subdomain)
                    self.links.append([each_wd, link, title])
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
    def run_subdomain(self, domain):
        threads = []
        for i in range(len(self.wds)):
            t = threading.Thread(target=self.get_subdomain, args=(domain, self.wds[i], i))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        print(list(set(self.resList)), self.links)
        return list(set(self.resList)), self.links


if __name__ == '__main__':
    a = BingSpider('nbcc.cn')
    a.run_subdomain('nbcc.cn')
