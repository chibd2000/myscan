# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 11:08

from spider.public import *
from spider import BaseSpider
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def getCurrentUrlList(links, suffixCompile):
    currentUrlList = []
    for link in links:  # 判断是不是一个新的网站
        url = link.get('href')
        # 根据特征值来进行判断，是否下面都不符合，那么就是一个完整的域名
        # href="/1.jpg"
        # href="javascript:alert(1)"
        _ = suffixCompile.search(str(url))
        if _ is None and _ is None:
            currentUrlList.append(str(url))  # 是的话 那么添加到result列表中
    return currentUrlList


class ParamSpider:
    """
    对于相关的动态脚本和js参数资产自己封装到这个类中进行使用
    """
    def __init__(self):
        self.source = 'ParamSpider'
        self.reqTimeout = 15
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    # learn from langzi
    async def getDynamicScriptLinks(self, session, domain, result):
        scriptLinks = []
        htmlLinks = []
        scriptFinaLinks = []
        htmlFinaLinks = []

        # http://www.bhxz.net/?list_7/
        # http://www.bhxz.net/?list_7

        for rurl in result:  # 再进行二次判断是不是子域名 这次的判断有三种情况
            if '//' in rurl and 'http' in rurl and domain in rurl:
                if '?' in rurl and '=' in rurl:
                    scriptLinks.append(rurl.strip())
                if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                    if '?' not in rurl:
                        htmlLinks.append(rurl.strip())
            if 'http' not in rurl and domain in rurl:
                # http 不在 domain 在
                if '?' in rurl and '=' in rurl:
                    scriptLinks.append('http://' + rurl.lstrip('/').strip())
                if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                    if '?' not in rurl:
                        htmlLinks.append(
                            'http://' + rurl.lstrip('/').strip())
            if 'http' not in rurl and domain not in rurl:
                # http 不在 domain 不在
                if '?' in rurl and '=' in rurl:
                    scriptLinks.append(
                        'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
                if '.html' in rurl or '.shtml' in rurl or '.htm' in rurl or '.shtm' in rurl:
                    if '?' not in rurl:
                        htmlLinks.append(
                            'http://' + domain.strip() + '/' + rurl.strip().lstrip('/'))
        print(htmlLinks, scriptLinks)
        # 判断爬取的参数是否存活
        # for x1 in htmlLinks:  # 对于爬取到的后缀是html等等参数链接进行二次处理 是否能够访问
        #     try:
        #         async with session.get(url=x1, timeout=self.reqTimeout, headers=self.headers,
        #                                verify_ssl=False) as resp1:
        #             if resp1 is not None and resp1.status == 200:
        #                 htmlFinaLinks.append(x1)
        #     except Exception as e:
        #         print('[-] curl {} error, the error is {}'.format(x1, e.args))
        #
        # for x2 in scriptLinks:  # 平常的id?=1 这种参数进行二次处理 是否能够访问
        #     try:
        #         async with session.get(url=x2, timeout=self.reqTimeout, headers=self.headers,
        #                                verify_ssl=False) as resp2:
        #             if resp2 is not None and resp2.status == 200:
        #                 if str(resp2.url).find('=') > 0:
        #                     scriptFinaLinks.append(x2)
        #     except Exception as e:
        #         print('[-] curl {} error, the error is {}'.format(x2, e.args))
        return self._flushLinks(scriptFinaLinks, htmlFinaLinks)

    """清洗数据"""
    def _flushLinks(self, scriptFinaLinks, htmlFinaLinks):
        dic_1 = []
        dic_2 = []
        dic_3 = []
        dic_4 = []
        for i in htmlFinaLinks:
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
        for i in scriptFinaLinks:
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
        return ididx, hthtx

    # learn from jsfinder
    async def getJavascriptLinks(self, session, domain, text):
        jsUrlList = self.extractURL(text)
        for aJs in jsUrlList:
            pass

    def extractURL(self, content):
        pattern_raw = r"""
              (?:"|')                               # Start newline delimiter
              (
                ((?:[a-zA-Z]{1,10}://|//)           # Match a scheme [a-Z]*1-10 or //
                [^"'/]{1,}\.                        # Match a domainname (any character + dot)
                [a-zA-Z]{2,}[^"']{0,})              # The domainextension and/or path
                |
                ((?:/|\.\./|\./)                    # Start with /,../,./
                [^"'><,;| *()(%%$^/\\\[\]]          # Next character can't be...
                [^"'><,;|()]{1,})                   # Rest of the characters can't be
                |
                ([a-zA-Z0-9_\-/]{1,}/               # Relative endpoint with /
                [a-zA-Z0-9_\-/]{1,}                 # Resource name
                \.(?:[a-zA-Z]{1,4}|action)          # Rest + extension (length 1-4 or action)
                (?:[\?|/][^"|']{0,}|))              # ? mark with parameters
                |
                ([a-zA-Z0-9_\-]{1,}                 # filename
                \.(?:php|asp|aspx|jsp|json|
                     action|html|js|txt|xml)             # . + extension
                (?:\?[^"|']{0,}|))                  # ? mark with parameters
              )
              (?:"|')                               # End newline delimiter
            """
        pattern = re.compile(pattern_raw, re.VERBOSE)
        result = re.finditer(pattern, str(content))
        if result == None:
            return None
        js_url = []
        for match in result:
            if match.group() not in js_url:
                js_url.append(match.group().strip('"').strip("'"))
        return js_url


class AliveSpider(BaseSpider):

    def __init__(self, domain, domainList, pbar):
        super().__init__()
        self.source = 'AliveSpider'
        self.detechHttpProtocalList = ['http', 'https']
        self.domain = domain
        self.domainList = domainList
        self.linkList = []  # 存储参数
        self.aliveList = []  # 最终存活域名
        self.paramSpider = ParamSpider()
        self.pbar = pbar
        self.titleCompile = re.compile(r'<title>(?P<result>[^<]+)</title>')
        self.suffixCompile = re.compile('\.(gz|zip|rar|iso|pdf|txt|3ds|3g2|3gp|7z|DS_Store|a|aac|adp|ai|aif|aiff|apk|ar|asf|au|avi|bak|bin|bk|bmp|btif|bz2|cab|caf|cgm|cmx|cpio|cr2|dat|deb|djvu|dll|dmg|dmp|dng|doc|docx|dot|dotx|dra|dsk|dts|dtshd|dvb|dwg|dxf|ear|ecelp4800|ecelp7470|ecelp9600|egg|eol|eot|epub|exe|f4v|fbs|fh|fla|flac|fli|flv|fpx|fst|fvt|g3|gif|gz|h261|h263|h264|ico|ief|image|img|ipa|iso|jar|jpeg|jpgv|jpm|jxr|ktx|lvp|lz|lzma|lzo|m3u|m4a|m4v|mar|mdi|mid|mj2|mka|mkv|mmr|mng|mov|movie|mp3|mp4|mp4a|mpeg|mpg|mpga|mxu|nef|npx|o|oga|ogg|ogv|otf|pbm|pcx|pdf|pea|pgm|pic|png|pnm|ppm|pps|ppt|pptx|ps|psd|pya|pyc|pyo|pyv|qt|rar|ras|raw|rgb|rip|rlc|rz|s3m|s7z|scm|scpt|sgi|shar|sil|smv|so|sub|swf|tar|tbz2|tga|tgz|tif|tiff|tlz|ts|ttf|uvh|uvi|uvm|uvp|uvs|uvu|viv|vob|war|wav|wax|wbmp|wdp|weba|webm|webp|whl|wm|wma|wmv|wmx|woff|woff2|wvx|xbm|xif|xls|xlsx|xlt|xm|xpi|xpm|xwd|xz|z|zip|zipx)|javascript|:;|#|%')

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

    async def _getAlive(self, semaphore, origin):
        # url = f'{detechHttpProtocal}://{origin}' if str(origin).startswith(('http:', 'https:')) is False else origin
        url = f'http://{origin}' if str(origin).startswith(('http:', 'https:')) is False else origin
        domain = url.split('//')[1].strip('/').replace('www.', '')
        try:
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, verify_ssl=False, timeout=60) as response:
                        if response is not None:
                            text = await response.text()
                            # print(text)
                            # 参数解析处理
                            soup = BeautifulSoup(text, 'lxml')
                            title = self._getTitle(soup)
                            links = soup.findAll('a')
                            status = response.status
                            frame = response.headers.get('X-Powered-By', '')
                            self.resList.append({'url': url, 'title': title, 'status': status, 'frame': frame})
                            # 如果能走到这里的话，可能虽然不是200，但是该网站是可以进行访问的
                            # SpringBoot一般就是这样，首页为404状态码 但是这种情况就不能跳过，还是需要进行保存
                            self.aliveList.append(origin)
                            result = getCurrentUrlList(links, self.suffixCompile)
                            if result:
                                result = list(set(result))
                                scriptFinaLinks, htmlFinaLinks = await self.paramSpider.getDynamicScriptLinks(session, domain, result)
                                if scriptFinaLinks:
                                    for scriptLink in scriptFinaLinks:
                                        self.linkList.append(scriptLink)
                                if htmlFinaLinks:
                                    for htmlLink in htmlFinaLinks:
                                        self.linkList.append(htmlLink.replace('.htm', '*.htm').replace('.shtm', '*.shtm'))
        except TimeoutError:
            print('[-] curl {} error, the error is Timeout.'.format(url))
        except ConnectionRefusedError:
            print('[-] curl {} error, the error is Connection Refused.'.format(url))
        except aiohttp.ClientPayloadError:
            # 协议问题导致的无法访问，这种情况下这个域名如果通过正常的浏览器访问还是可以正常访问的
            self.resList.append({'url': url, 'title': '', 'status': '手动访问', 'frame': ''})
            print('[-] curl {} error, the error is payloadError, check HTTP 1.1.'.format(url))
        except Exception as e:
            # self.resList.append({'url': url, 'title': '', 'status': '无法访问', 'frame': ''})
            print('[-] curl {} error.'.format(url))
        finally:
            self.pbar.update(1)

    async def _getBackend(self, semaphore, origin):
        """
        这个想法是看到大师兄代码里面的，然后自己觉得也有必要添加，原因是后台管理
        也算是敏感的资产后面通过WebCrack可以快速的实现相关基于后台的弱口令探测
        """
        pass

    def _getTitle(self, soup):
        """
        这个方法后面加的，我发现如果简单的通过正则来获取标题title的话获取的不完全，虽然把信息搜集过来了，但是如果主要的标题看不见的话，
        还是需要去访问来观察，有时候如果标题获取的完全的话，那么就能更多的省去访问的时间
        """
        title = soup.title
        if title:
            return title.text

        # for springboot
        h1 = soup.h1
        if h1:
            return h1.text

        h2 = soup.h2
        if h2:
            return h2.text

        h3 = soup.h3
        if h2:
            return h3.text

        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc.get('content')

        word = soup.find('meta', attrs={'name': 'keywords'})
        if word:
            return word.get('content')

        text = soup.text
        if len(text) <= 200:
            return text

        return ''

    async def spider(self):
        concurrency = 500  # 这里的话稍微控制下并发量
        semaphore = asyncio.Semaphore(concurrency)
        await asyncio.gather(*[asyncio.create_task(self._getAlive(semaphore, i)) for i in self.domainList])
        self.linkList = list(set(self.linkList))
        self.aliveList = list(set(self.aliveList))
        self.writeFile(getUniqueList(self.resList), 14)

    async def main(self):
        await self.spider()
        print(self.linkList)
        return self.linkList, self.aliveList


if __name__ == '__main__':
    from tqdm import tqdm

    pbar = tqdm(total=len(['geely.com']), desc='[{}]'.format('geely.com'), ncols=100)
    alive = AliveSpider('geely.com', ['http://guofeng1024.58food.com/'], pbar)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(alive.main())
