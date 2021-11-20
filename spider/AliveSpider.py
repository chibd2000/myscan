# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 11:08

from spider.public import *
from spider import BaseSpider
from urllib.parse import urlparse
from bs4 import BeautifulSoup


# js 爬取 @小洲师傅 @jsFinder
def getJavascriptLinks():
    pass


def getCurrentUrlList(links, suffixCompile):
    currentUrlList = []
    for link in links:  # 判断是不是一个新的网站
        url = link.get('href')
        # 根据特征值来进行判断，是否下面都不符合，那么就是一个完整的域名
        # href="/1.jpg"
        # href="javascript:alert(1)"
        _ = suffixCompile.search(str(url))
        if _ is None and _ is None:
            currentUrlList.append(str(_))  # 是的话 那么添加到result列表中
    return currentUrlList

class AliveSpider(BaseSpider):

    def __init__(self, domain, domainList, pbar):
        super().__init__()
        self.source = 'AliveSpider'
        self.domain = domain
        self.domainList = domainList
        self.linkList = []  # 存储参数
        self.aliveList = []  # 最终存活域名
        self.pbar = pbar
        self.titleCompile = re.compile(r'<title>(.*?)</title>')
        self.suffixCompile = re.compile(r'.(jpg|png|bmp|mp3|wma|wmv|gz|zip|rar|iso|pdf|txt)|javascript|:;|#|%')

    def writeFile(self, web_lists, page):
        try:
            workbook = openpyxl.load_workbook(abs_path + str(self.domain) + ".xlsx")
            worksheet = workbook.worksheets[page]
            index = 0
            while index < len(web_lists):
                web = list()
                web.append(web_lists[index]['url'])
                web.append(web_lists[index]['status'])
                web.append(web_lists[index]['title'])
                web.append(web_lists[index]['frame'])
                worksheet.append(web)
                index += 1
            workbook.save(abs_path + str(self.domain) + ".xlsx")
            workbook.close()
        except Exception as e:
            print('[-] [{}] writeFile error, error is {}'.format(self.source, e.__str__()))

    async def getAlive(self, semaphore, originUrl):
        result = []
        idid = []
        htht = []
        url = f'https://{originUrl}' if str(originUrl).startswith(('http:', 'https:')) is False else originUrl
        domain = url.split('//')[1].strip('/').replace('www.', '')
        try:
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, verify_ssl=False,
                                           timeout=self.reqTimeout) as response:
                        if response is not None:
                            text = await response.text()
                            try:
                                title = self.titleCompile.search(text, re.S | re.I)[1].strip(' ').strip('\r\n').strip(
                                    '\n').strip('\r')
                            except Exception:
                                title = ''
                            status = response.status
                            frame = response.headers.get('X-Powered-By', '')
                            self.resList.append({'url': url, 'title': title, 'status': status, 'frame': frame})
                            # 如果能走到这里的话，可能虽然不是200，但是该网站是可以进行访问的
                            # SpringBoot一般就是这样，首页为404状态码 但是这种情况就不能跳过，还是需要进行保存
                            self.aliveList.append(originUrl)
                            # 参数解析处理
                            soup = BeautifulSoup(text, 'html.parser')
                            links = soup.findAll('a')
                            result = getCurrentUrlList(links, self.suffixCompile)
                            if result:
                                result = list(set(result))
                                await self.getDynamicScriptLinks(session, domain, result)

                                # 整合数据
                                dic_1 = []
                                dic_2 = []
                                dic_3 = []
                                dic_4 = []
                                for i in htht:
                                    path = urlparse(i).path
                                    if path.count('/') == 1:
                                        dic_1.append(i)
                                    if path.count('/') == 2:
                                        dic_2.append(i)
                                    if path.count('/') == 3:
                                        dic_3.append(i)
                                    if path.count('/') > 3:
                                        dic_4.append(i)
                                hthtx = []
                                ididx = []
                                if dic_1:
                                    hthtx.append(random.choice(dic_1))
                                if dic_2:
                                    hthtx.append(random.choice(dic_2))
                                if dic_3:
                                    hthtx.append(random.choice(dic_3))
                                if dic_4:
                                    hthtx.append(random.choice(dic_4))
                                dic_11 = []
                                dic_21 = []
                                dic_31 = []
                                dic_41 = []
                                for i in idid:
                                    path = urlparse(i).path
                                    if path.count('/') == 1:
                                        dic_11.append(i)
                                    if path.count('/') == 2:
                                        dic_21.append(i)
                                    if path.count('/') == 3:
                                        dic_31.append(i)
                                    if path.count('/') > 3:
                                        dic_41.append(i)
                                if dic_11:
                                    ididx.append(random.choice(dic_11))
                                if dic_21:
                                    ididx.append(random.choice(dic_21))
                                if dic_31:
                                    ididx.append(random.choice(dic_31))
                                if dic_41:
                                    ididx.append(random.choice(dic_41))
                            if ididx:
                                for i in ididx:
                                    self.linkList.append(i)
                            if hthtx:
                                for u in hthtx:
                                    self.linkList.append(u.replace('.htm', '*.htm').replace('.shtm', '*.shtm'))
        except aiohttp.ClientPayloadError as e:
            print('[-] curl {} error, the error is timeout'.format(url))
        except Exception as e:
            self.resList.append({'url': url, 'title': '', 'status': '无法访问', 'frame': ''})
            print('[-] curl {} error, the error is {}'.format(url, e.__str__()))
        finally:
            self.pbar.update(1)

    # sql参数爬取@langzi
    async def getDynamicScriptLinks(self, session, domain, result):
        scriptLinks = []
        htmlLinks = []
        scriptFinaLinks = []
        htmlFinaLinks = []

        for rurl in result:  # 再进行二次判断是不是子域名 这次的判断有三种情况
            if '//' in rurl and 'http' in rurl and domain in rurl:
                # http // domain 都在
                # https://www.yamibuy.com/cn/search.php?tags=163
                # http://news.hnu.edu.cn/zhyw/2017-11-11/19605.html
                if '?' in rurl and '=' in rurl:
                    # result_links.append(rurl)
                    scriptLinks.append(rurl.strip())
                if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                    if '?' not in rurl:
                        # result_links.append(rurl)
                        htmlLinks.append(rurl.strip())
            # //wmw.dbw.cn/system/2018/09/25/001298805.shtml
            if 'http' not in rurl and domain in rurl:
                # http 不在 domain 在
                if '?' in rurl and '=' in rurl:
                    scriptLinks.append('http://' + rurl.lstrip('/').strip())
                if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                    if '?' not in rurl:
                        htmlLinks.append(
                            'http://' + rurl.lstrip('/').strip())
            # /chanpin/2018-07-12/3.html"
            if 'http' not in rurl and domain not in rurl:
                # http 不在 domain 不在
                if '?' in rurl and '=' in rurl:
                    scriptLinks.append(
                        'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
                if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                    if '?' not in rurl:
                        htmlLinks.append(
                            'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))

        # 判断爬取的参数是否存活
        for x1 in htmlLinks:  # 对于爬取到的后缀是html等等参数链接进行二次处理 是否能够访问
            try:
                async with session.get(url=x1, timeout=self.reqTimeout, headers=self.headers,
                                       verify_ssl=False) as resp1:
                    if resp1 is not None and resp1.status == 200:
                        htmlFinaLinks.append(x1)
            except Exception as e:
                print('[-] curl {} error, the error is {}'.format(x1, e.__str__()))

        for x2 in scriptLinks:  # 平常的id?=1 这种参数进行二次处理 是否能够访问
            try:
                async with session.get(url=x2, timeout=self.reqTimeout, headers=self.headers,
                                       verify_ssl=False) as resp2:
                    if resp2 is not None and resp2.status == 200:
                        if str(resp2.url).find('=') > 0:
                            scriptFinaLinks.append(x2)
            except Exception as e:
                print('[-] curl {} error, the error is {}'.format(x2, e.__str__()))
        return scriptFinaLinks, htmlFinaLinks

    async def spider(self):
        concurrency = 500  # 这里的话稍微控制下并发量
        semaphore = asyncio.Semaphore(concurrency)
        await asyncio.gather(*[asyncio.create_task(self.getAlive(semaphore, i)) for i in self.domainList])
        self.linkList = list(set(self.linkList))
        self.aliveList = list(set(self.aliveList))
        # self.writeFile(getUniqueList(self.resList), 14)

    async def main(self):
        await self.spider()
        print(self.aliveList)
        return self.linkList, self.aliveList


if __name__ == '__main__':
    from tqdm import tqdm

    pbar = tqdm(total=len(['172-18-0-44-8080.webvpn.nbcc.cn']), desc='[{}]'.format('aliveSpider'), ncols=100)
    alive = AliveSpider('zjhu.edu.cn', ['172-18-0-44-8080.webvpn.nbcc.cn'], pbar)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(alive.main())
