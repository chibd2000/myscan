# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 11:08

from spider.public import *
from spider import BaseSpider
from urllib.parse import urlparse
from bs4 import BeautifulSoup


# js 爬取 @小洲师傅
class JSSpider:
    pass


# sql参数爬取
class ParamsLinkSpider:
    pass
    # @staticmethod
    # def getLinks(url):
    #     # 1、https://www.yamibuy.com/cn/brand.php?id=566
    #     # 2、http://www.labothery-tea.cn/chanpin/2018-07-12/4.html
    #
    #     # if 'gov.cn' in self.url:
    #     #     return 0
    #     #     pass
    #     # http://www.baidu.com/ -> www.baidu.com/ -> www.baidu.com -> baidu.com
    #     domain = url.split('//')[1].strip('/').replace('www.', '')
    #     result = []
    #     id_links = []
    #     html_links = []
    #     result_links = {}
    #     html_links_s = []
    #     result_links['title'] = '网址标题获取失败'
    #     idid = []
    #     htht = []
    #     try:
    #         rxww = requests.get(url, headers=self.headers, verify=False, timeout=self.reqTimeout)
    #         soup = BeautifulSoup(rxww.content, 'html.parser', from_encoding='iso-8859-1')
    #
    #         try:
    #             encoding = requests.utils.get_encodings_from_content(rxww.text)[0]
    #             res = rxww.content.decode(encoding, 'replace')
    #             title_pattern = '<title>(.*?)</title>'
    #             title = re.search(title_pattern, res, re.S | re.I)
    #             result_links['title'] = str(title.group(1))
    #         except:
    #             pass
    #
    #         if result_links['title'] == '' or result_links['title'] == None:
    #             result_links['title'] = '网址标题获取失败'
    #
    #         links = soup.findAll('a')
    #         for link in links:  # 判断是不是一个新的网站
    #             _url = link.get('href')
    #             res = re.search('(javascript|:;|#|%)', str(_url))
    #             res1 = re.search(
    #                 '.(jpg|png|bmp|mp3|wma|wmv|gz|zip|rar|iso|pdf|txt)', str(_url))
    #             if res == None and res1 == None:
    #                 result.append(str(_url))  # 是的话 那么添加到result列表中
    #             else:
    #                 pass
    #         # print(result)
    #         # time.sleep(50)
    #         if result != []:
    #             rst = list(set(result))
    #             for rurl in rst:  # 再进行二次判断是不是子域名 这次的判断有三种情况
    #                 if '//' in rurl and 'http' in rurl and domain in rurl:
    #                     # http // domain 都在
    #                     # https://www.yamibuy.com/cn/search.php?tags=163
    #                     # http://news.hnu.edu.cn/zhyw/2017-11-11/19605.html
    #                     if '?' in rurl and '=' in rurl:
    #                         # result_links.append(rurl)
    #                         id_links.append(rurl.strip())
    #                     if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
    #                         if '?' not in rurl:
    #                             # result_links.append(rurl)
    #                             html_links.append(rurl.strip())
    #                 # //wmw.dbw.cn/system/2018/09/25/001298805.shtml
    #                 if 'http' not in rurl and domain in rurl:
    #                     # http 不在    domain 在
    #                     if '?' in rurl and '=' in rurl:
    #                         id_links.append('http://' + rurl.lstrip('/').strip())
    #                     if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
    #                         if '?' not in rurl:
    #                             html_links.append(
    #                                 'http://' + rurl.lstrip('/').strip())
    #
    #                 # /chanpin/2018-07-12/3.html"
    #                 if 'http' not in rurl and domain not in rurl:
    #                     # http 不在  domain 不在
    #                     if '?' in rurl and '=' in rurl:
    #                         id_links.append(
    #                             'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
    #                     if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
    #                         if '?' not in rurl:
    #                             html_links.append(
    #                                 'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
    #
    #             # print(html_links)
    #             # print(id_links)
    #             # time.sleep(50)
    #
    #             for x1 in html_links:  # 对于爬取到的后缀是html等等参数链接进行二次处理 是否能够访问
    #                 try:
    #                     rx1 = requests.get(url=x1, headers=self.headers, timeout=self.reqTimeout)
    #                     if rx1.status_code == 200:
    #                         htht.append(x1)
    #                 except Exception as e:
    #                     print('error, {}'.format(e.args))
    #
    #             for x2 in id_links:  # 平常的id?=1 这种参数进行二次处理 是否能够访问
    #                 try:
    #                     rx2 = requests.get(url=x2, headers=self.headers, timeout=self.reqTimeout)
    #                     if rx2.status_code == 200:
    #                         if rx2.url.find('=') > 0:
    #                             idid.append(rx2.url)
    #                 except Exception as e:
    #                     print('error, {}'.format(e.args))
    #
    #             hthtx = []
    #             ididx = []
    #             dic_1 = []
    #             dic_2 = []
    #             dic_3 = []
    #             dic_4 = []
    #             for i in htht:
    #                 path = urlparse(i).path
    #                 if path.count('/') == 1:
    #                     dic_1.append(i)
    #                 if path.count('/') == 2:
    #                     dic_2.append(i)
    #                 if path.count('/') == 3:
    #                     dic_3.append(i)
    #                 if path.count('/') > 3:
    #                     dic_4.append(i)
    #             if dic_1:
    #                 hthtx.append(random.choice(dic_1))
    #             if dic_2:
    #                 hthtx.append(random.choice(dic_2))
    #             if dic_3:
    #                 hthtx.append(random.choice(dic_3))
    #             if dic_4:
    #                 hthtx.append(random.choice(dic_4))
    #             dic_11 = []
    #             dic_21 = []
    #             dic_31 = []
    #             dic_41 = []
    #             for i in idid:
    #                 path = urlparse(i).path
    #                 if path.count('/') == 1:
    #                     dic_11.append(i)
    #                 if path.count('/') == 2:
    #                     dic_21.append(i)
    #                 if path.count('/') == 3:
    #                     dic_31.append(i)
    #                 if path.count('/') > 3:
    #                     dic_41.append(i)
    #             if dic_11:
    #                 ididx.append(random.choice(dic_11))
    #             if dic_21:
    #                 ididx.append(random.choice(dic_21))
    #             if dic_31:
    #                 ididx.append(random.choice(dic_31))
    #             if dic_41:
    #                 ididx.append(random.choice(dic_41))
    #
    #             if hthtx == []:
    #                 pass
    #             else:
    #                 result_links['html_links'] = hthtx
    #
    #             if ididx == []:
    #                 pass
    #             else:
    #                 result_links['id_links'] = ididx
    #
    #         with open('test.txt', 'a+', encoding='utf-8')as a:
    #             if ididx:
    #                 for i in ididx:
    #                     a.write(i + '\n')
    #             if hthtx:
    #                 for u in hthtx:
    #                     a.write(u.replace('.htm', '*.htm').replace('.shtm', '*.shtm') + '\n')
    #
    #         if result_links == {}:
    #             return None
    #         else:
    #             return result_links
    #
    #     except Exception as e:
    #         print('error, {}'.format(e.args))
    #         pass
    #     return None


class AliveSpider(BaseSpider):

    def __init__(self, domain, domainList, pbar):
        super().__init__()
        self.source = 'AliveSpider'
        self.domain = domain
        self.domainList = domainList
        self.linkList = []  # 存储参数
        self.aliveList = []  # 最终存活域名
        self.pbar = pbar
        self.titleCompile = re.compile('<title>(.*?)</title>')

    def writeFile(self, web_lists, page):
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

    async def getLinks(self, semaphore, originUrl):
        result = []
        id_links = []
        html_links = []
        idid = []
        htht = []
        url = f'https://{originUrl}' if str(originUrl).startswith(('http:', 'https:')) is False else originUrl
        domain = url.split('//')[1].strip('/').replace('www.', '')
        try:
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, verify_ssl=False) as response:
                        if response is not None and response.status == 200:
                            self.aliveList.append(originUrl)
                            hthtx = []
                            ididx = []
                            text = await response.text()
                            # print(text)
                            soup = BeautifulSoup(text, 'html.parser')
                            # title
                            try:
                                title = self.titleCompile.search(text, re.S | re.I)[1].strip(' ').strip('\r\n').strip(
                                    '\n').strip('\r')
                            except Exception:
                                title = ''
                            # status
                            status = response.status
                            # frame
                            frame = response.headers.get('X-Powered-By', '')
                            self.resList.append({'url': url, 'title': title, 'status': status, 'frame': frame})

                            links = soup.findAll('a')
                            for link in links:  # 判断是不是一个新的网站
                                _url = link.get('href')
                                res = re.search('(javascript|:;|#|%)', str(_url))
                                res1 = re.search('.(jpg|png|bmp|mp3|wma|wmv|gz|zip|rar|iso|pdf|txt)', str(_url))
                                if res is None and res1 is None:
                                    result.append(str(_url))  # 是的话 那么添加到result列表中

                            if result:
                                rst = list(set(result))
                                for rurl in rst:  # 再进行二次判断是不是子域名 这次的判断有三种情况
                                    if '//' in rurl and 'http' in rurl and domain in rurl:
                                        # http // domain 都在
                                        # https://www.yamibuy.com/cn/search.php?tags=163
                                        # http://news.hnu.edu.cn/zhyw/2017-11-11/19605.html
                                        if '?' in rurl and '=' in rurl:
                                            # result_links.append(rurl)
                                            id_links.append(rurl.strip())
                                        if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                                            if '?' not in rurl:
                                                # result_links.append(rurl)
                                                html_links.append(rurl.strip())
                                    # //wmw.dbw.cn/system/2018/09/25/001298805.shtml
                                    if 'http' not in rurl and domain in rurl:
                                        # http 不在 domain 在
                                        if '?' in rurl and '=' in rurl:
                                            id_links.append('http://' + rurl.lstrip('/').strip())
                                        if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                                            if '?' not in rurl:
                                                html_links.append(
                                                    'http://' + rurl.lstrip('/').strip())
                                    # /chanpin/2018-07-12/3.html"
                                    if 'http' not in rurl and domain not in rurl:
                                        # http 不在 domain 不在
                                        if '?' in rurl and '=' in rurl:
                                            id_links.append(
                                                'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
                                        if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                                            if '?' not in rurl:
                                                html_links.append(
                                                    'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
                                for x1 in html_links:  # 对于爬取到的后缀是html等等参数链接进行二次处理 是否能够访问
                                    try:
                                        async with session.get(url=x1, timeout=self.reqTimeout, headers=self.headers,
                                                               verify_ssl=False) as resp1:
                                            if resp1 is not None and resp1.status == 200:
                                                htht.append(x1)
                                    except Exception as e:
                                        print('[-] curl {} error, the error is {}'.format(x1, e.__str__()))

                                for x2 in id_links:  # 平常的id?=1 这种参数进行二次处理 是否能够访问
                                    try:
                                        async with session.get(url=x2, timeout=self.reqTimeout, headers=self.headers,
                                                               verify_ssl=False) as resp2:
                                            if resp2 is not None and resp2.status == 200:
                                                if str(resp2.url).find('=') > 0:
                                                    idid.append(x2)
                                    except Exception as e:
                                        print('[-] curl {} error, the error is {}'.format(x2, e.__str__()))

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

    async def spider(self):
        concurrency = 500  # 这里的话稍微控制下并发量
        semaphore = asyncio.Semaphore(concurrency)
        await asyncio.gather(*[asyncio.create_task(self.getLinks(semaphore, i)) for i in self.domainList])
        self.linkList = list(set(self.linkList))
        self.aliveList = list(set(self.aliveList))
        self.writeFile(getUniqueList(self.resList), 12)

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
