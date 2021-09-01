# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 11:08
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from spider.BaseSpider import *


# def getUniqueList(L):
#     (output, temp) = ([], [])
#     for l in L:
#         for k, v in l.items():
#             flag = False
#             if (k, v) not in temp:
#                 flag = True
#                 break
#         if flag:
#             output.append(l)
#         temp.extend(l.items())
#     return output
class AliveSpider(Spider):
    def __init__(self, domain, domainList):
        super().__init__()
        self.source = 'ip2domain'
        self.domain = domain
        self.domainList = domainList
        self.linkList = []

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

    async def getLinks(self, semaphore, aaaa):
        url = f'http://{aaaa}' if str(aaaa).startswith(('http:', 'https:')) is False else aaaa
        domain = url.split('//')[1].strip('/').replace('www.', '')
        result = []
        id_links = []
        html_links = []
        idid = []
        htht = []
        try:
            async with semaphore:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(url) as resp:
                        hthtx = []
                        ididx = []
                        text = await resp.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        # 标题
                        title_pattern = '<title>(.*?)</title>'
                        try:
                            title = re.search(title_pattern, text, re.S | re.I)[1].strip(' ').strip('\r\n').strip('\n').strip('\r')
                        except:
                            title = ''
                        # status
                        status = resp.status
                        # frame
                        frame = resp.headers.get('X-Powered-By', '')
                        self.resList.append({'url': str(url), 'title': title, 'status': status, 'frame': frame})
                        links = soup.findAll('a')
                        for link in links:  # 判断是不是一个新的网站
                            _url = link.get('href')
                            res = re.search('(javascript|:;|#|%)', str(_url))
                            res1 = re.search('.(jpg|png|bmp|mp3|wma|wmv|gz|zip|rar|iso|pdf|txt)', str(_url))
                            if res is None and res1 is None:
                                result.append(str(_url))  # 是的话 那么添加到result列表中
                            else:
                                pass
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
                                    async with session.get(x1) as resp1:
                                        if resp1.status == 200:
                                            htht.append(x1)
                                except Exception as e:
                                    print('[-] curl {} error.'.format(x1))

                            for x2 in id_links:  # 平常的id?=1 这种参数进行二次处理 是否能够访问
                                try:
                                    async with session.get(x2) as resp2:
                                        if resp2.status == 200:
                                            if str(resp2.url).find('=') > 0:
                                                idid.append(x2)
                                except Exception as e:
                                    print('[-] curl {} error.'.format(x2))
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
        except Exception as e:
            self.resList.append({'url': url, 'title': '', 'status': '无法访问', 'frame': ''})
            print('[-] curl error is {}'.format(e.args))

    async def spider(self):
        concurrency = 500  # 这里的话稍微控制下并发量
        semaphore = asyncio.Semaphore(concurrency)

        await asyncio.gather(*[asyncio.create_task(self.getLinks(semaphore, i)) for i in self.domainList])
        self.linkList = list(set(self.linkList))
        self.writeFile(getUniqueList(self.resList), 11)

    async def main(self):
        await self.spider()
        return self.linkList


if __name__ == '__main__':
    alive = AliveSpider('zjhu.edu.cn', ['mkszyxy.zjhu.edu.cn', 'shhzc.zjhu.edu.cn',
                                        'yjsy.zjhu.edu.cn',
                                        'jy.zjhu.edu.cn',
                                        'www.jy.zjhu.edu.cn',
                                        'cgzx.zjhu.edu.cn',
                                        'mh.zjhu.edu.cn:5008',
                                        'xcglc.zjhu.edu.cn',
                                        'https://rz.zjhu.edu.cn',
                                        'english.zjhu.edu.cn',
                                        'smkxxy.zjhu.edu.cn',
                                        'xyw.zjhu.edu.cn',
                                        'ysxy.zjhu.edu.cn',
                                        'anding.zjhu.edu.cn'])
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(alive.main())
    print(res)
