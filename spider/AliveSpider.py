# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 11:08
from core.public import *
from core.parser.urlparser import urlParser
from core.utils.differ import DifferentChecker
from spider import BaseSpider
from bs4 import BeautifulSoup


def getCurrentUrlList(links, suffixCompile):
    currentUrlList = []
    for link in links:
        aLink = link.get('href')
        if aLink is not None:
            _ = suffixCompile.search(str(aLink))
            if _ is None:
                currentUrlList.append(str(aLink))  # 是的话 那么添加到result列表中
    return currentUrlList


class ParamSpider:
    """
    对于相关的动态脚本和js参数资产自己封装到这个类中进行使用
    write in 2021.11.21 12.03 @zpchcbd
    """
    def __init__(self):
        self.source = 'ParamSpider'
        self.reqTimeout = 15
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    # learn from jsFinder / langzi.fun
    async def getDynamicScriptLinks(self, session, url, linkList):
        """实现动态脚本参数的获取"""
        scriptLinks = []
        htmlLinks = []
        urlparser = urlParser(url)
        """分别识别伪静态和动态链接"""
        for link in linkList:  # 再进行二次判断是不是子域名 这次的判断有三种情况
            if link.startswith('http') and '://' in link and urlparser.subdomain in link and '.js?' not in link and '.min.js' not in link:
                # http://www.baidu.com
                if '?' in link and '=' in link:
                    # result_links.append(rurl)
                    scriptLinks.append(link.strip())
                if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                    if '?' not in link:
                        # result_links.append(rurl)
                        htmlLinks.append(link.strip())

            if 'http' not in link and urlparser.subdomain in link and '.js?' not in link and '.min.js' not in link:
                if 'www' in url:
                    if 'www' in link:
                        if '?' in link and '=' in link:
                            scriptLinks.append(urlparser.scheme + link.lstrip('/').lstrip('.').rstrip('/').rstrip('.').replace('//','').replace(':', ''))
                        if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                            if '?' not in link:
                                # result_links.append(rurl)
                                htmlLinks.append(urlparser.scheme + link.lstrip('/').lstrip('.').rstrip('/').rstrip('.').replace('//','').replace(':', ''))
                    else:
                        if '?' in link and '=' in link:
                            scriptLinks.append(urlparser.scheme + 'www.' + link.lstrip('/').lstrip('.').rstrip('/').rstrip('.').replace('//','').replace(':', ''))
                        if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                            if '?' not in link:
                                htmlLinks.append(urlparser.scheme + 'www.' + link.lstrip('/').lstrip('.').rstrip('/').rstrip('.').replace('//', '').replace(':', ''))
                else:
                    if '?' in link and '=' in link:
                        scriptLinks.append(urlparser.scheme + link.lstrip('/').lstrip('.').rstrip('/').rstrip('.').replace('//', '').replace(':', ''))
                    if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                        if '?' not in link:
                            htmlLinks.append(urlparser.scheme + link.lstrip('/').lstrip('.').rstrip('/').rstrip('.').replace('//','').replace(':', ''))

            if 'http' not in link and urlparser.subdomain not in link and ':' not in link and '//' not in link and '.js?' not in link and '.min.js' not in link:
                # /sttd/xhm/
                if '?' in link and '=' in link:
                    scriptLinks.append(urlparser.scheme + urlparser.subdomain + '/' + link.lstrip('/').lstrip('.').rstrip('/').rstrip('.').replace('//', '').replace(':', ''))
                if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                    if '?' not in link:
                        htmlLinks.append(urlparser.scheme + urlparser.subdomain + '/' + link.lstrip('/').lstrip('.').rstrip('/').rstrip('.').replace('//', '').replace(':', ''))

            if link.startswith('://') and 'http' not in link and urlparser.subdomain in link and '.js?' not in link and '.min.js' not in link:
                if '?' in link and '=' in link:
                    scriptLinks.append(urlparser.scheme + link.replace('://', ''))
                if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                    if '?' not in link:
                        htmlLinks.append(urlparser.scheme + link.replace('://', ''))

            if link.startswith('//') and urlparser.subdomain in link and '.js?' not in link and '.min.js' not in link:
                # //order.jd.com/center/list.action
                if '?' in link and '=' in link:
                    scriptLinks.append(urlparser.scheme + link.replace('//', ''))
                if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                    if '?' not in link:
                        htmlLinks.append(urlparser.scheme + link.replace('//', ''))

            if '//' in link and link.startswith('http') and urlparser.subdomain in link and '.js?' not in link and '.min.js' not in link:
                # http // domain 都在
                # https://www.yamibuy.com/cn/search.php?tags=163
                # http://news.hnu.edu.cn/zhyw/2017-11-11/19605.html
                if '?' in link and '=' in link:
                    scriptLinks.append(link.strip())
                if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                    if '?' not in link:
                        htmlLinks.append(link.strip())
            # //wmw.dbw.cn/system/2018/09/25/001298805.shtml
            if 'http' not in link and urlparser.subdomain in link and '.js?' not in link and '.min.js' not in link:
                # http 不在    domain 在
                if '?' in link and '=' in link:
                    scriptLinks.append(urlparser.scheme + link.lstrip('/').lstrip('.').strip().lstrip('/'))
                if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                    if '?' not in link:
                        htmlLinks.append(urlparser.scheme + link.lstrip('/').lstrip('.').strip().lstrip('/'))

            # /chanpin/2018-07-12/3.html"
            if 'http' not in link and urlparser.subdomain not in link and '.js?' not in link and '.min.js' not in link:
                # http 不在  domain 不在
                if '?' in link and '=' in link:
                    scriptLinks.append(urlparser.scheme + urlparser.subdomain.strip() + '/' + link.strip().lstrip('/').lstrip('.').lstrip('/'))
                if '.html' in link or '.shtml' in link or '.htm' in link or '.shtm' in link:
                    if '?' not in link:
                        htmlLinks.append(urlparser.scheme + urlparser.subdomain.strip() + '/' + link.strip().lstrip('/').lstrip('.').lstrip('/'))

        scriptFinaList = self._flushLinks(scriptLinks)
        htmlFinaList = self._flushLinks(htmlLinks)

        """判断爬取的参数是否存活"""
        # htmlFinaLinks = []
        # scriptFinaLinks = []
        # for x1 in htmlLinks:  # 伪静态是否能够访问
        #     try:
        #         async with session.get(url=x1, timeout=self.reqTimeout, headers=self.headers, verify_ssl=False) as response:
        #             if response is not None and response.status == 200:
        #                 htmlFinaLinks.append(x1)
        #     except Exception as e:
        #         print('[-] curl {} error, the error is {}'.format(x1, e.args))
        #
        # for x2 in scriptLinks:  # 动态脚本参数是否能够访问
        #     try:
        #         async with session.get(url=x2, timeout=self.reqTimeout, headers=self.headers, verify_ssl=False) as response:
        #             if response is not None and response.status == 200:
        #                 if str(response.url).find('=') > 0:
        #                     scriptFinaLinks.append(x2)
        #     except Exception as e:
        #         print('[-] curl {} error, the error is {}'.format(x2, e.args))
        return scriptFinaList, htmlFinaList

    def _flushLinks(self, links):
        """匹配相似度清洗数据 write in 2021.11.24 15.48"""
        resList = []
        linkIndex = 0
        while linkIndex < len(links):
            current = links[linkIndex]
            goodIndexList = DifferentChecker.getCloseMatchIndex(current, links, n=10000, cutoff=0.9)
            currentResultList = []
            for index in reversed(sorted(goodIndexList)):
                currentResultList.append(links[index])
                del links[index]
            resList.append(currentResultList[0])
            linkIndex += 1
        return resList

    # learn from jsfinder
    async def getJavascriptLinks(self, session, domain, text):
        """实现javascript参数的获取 特征"/static/js/app" "/static/js/main"  """
        jsUrlList = self.extract_URL(text)
        for aJs in jsUrlList:
            pass


class AliveSpider(BaseSpider):

    def __init__(self, domain, domainList, pbar):
        super().__init__()
        self.source = 'AliveSpider'
        # self.detechHttpProtocalList = ['http', 'https']
        self.backendKeywordList = ['/admin', '/login', '/manage', '/system']
        self.domain = domain
        self.domainList = domainList
        self.pbar = pbar
        self.linkList = []  # 存储参数
        self.aliveList = []  # 最终存活域名
        self.paramSpider = ParamSpider()
        self.titleCompile = re.compile(r'<title>(?P<result>[^<]+)</title>')
        self.suffixCompile = re.compile(r'\.(gz|zip|rar|iso|pdf|txt|3ds|3g2|3gp|7z|DS_Store|a|aac|adp|ai|aif|aiff|apk|ar|asf|au|avi|bak|bin|bk|bmp|btif|bz2|cab|caf|cgm|cmx|cpio|cr2|dat|deb|djvu|dll|dmg|dmp|dng|doc|docx|dot|dotx|dra|dsk|dts|dtshd|dvb|dwg|dxf|ear|ecelp4800|ecelp7470|ecelp9600|egg|eol|eot|epub|exe|f4v|fbs|fh|fla|flac|fli|flv|fpx|css|fst|fvt|g3|gif|gz|h261|h263|h264|ico|ief|image|img|ipa|iso|jar|jpg|jpeg|jpgv|jpm|jxr|ktx|lvp|lz|lzma|lzo|m3u|m4a|m4v|mar|mdi|mid|mj2|mka|mkv|mmr|mng|mov|movie|mp3|mp4|mp4a|mpeg|mpg|mpga|mxu|nef|npx|o|oga|ogg|ogv|otf|pbm|pcx|pdf|pea|pgm|pic|png|pnm|ppm|pps|ppt|pptx|ps|psd|pya|pyc|pyo|pyv|qt|rar|ras|raw|rgb|rip|rlc|rz|s3m|s7z|scm|scpt|sgi|shar|sil|smv|so|sub|swf|tar|tbz2|tga|tgz|tif|tiff|tlz|ts|ttf|uvh|uvi|uvm|uvp|uvs|uvu|viv|vob|war|wav|wax|wbmp|wdp|weba|webm|webp|whl|wm|wma|wmv|wmx|woff|woff2|wvx|xbm|xif|xls|xlsx|xlt|xm|xpi|xpm|xwd|xz|z|zip|zipx)|javascript|:;|#|%')
        self.beckendCompile = re.compile('(登录|后台|管理|系统|admin|Manage.?)')

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

    async def _getAlive(self, semaphore, domain):
        url = f'http://{domain}' if domain.startswith(('http://', 'https://')) is False else domain
        try:
            async with semaphore:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, verify_ssl=False, timeout=60) as response:
                        if response is not None:
                            text = await response.text()
                            soup = BeautifulSoup(text, 'lxml')
                            title = self._getTitle(soup)
                            status = response.status
                            frame = response.headers.get('X-Powered-By', '')
                            self.resList.append({'url': url, 'title': title, 'status': status, 'frame': frame})
                            """
                            如果能走到这里的话，可能虽然不是200，但是该网站是可以进行访问的
                            SpringBoot一般就是这样，首页为404状态码但是这种情况就不能跳过,还是需要进行保存
                            """
                            self.aliveList.append(domain)
                            links = soup.findAll('a')
                            result = getCurrentUrlList(links, self.suffixCompile)
                            if result:
                                result = list(set(result))
                                scriptFinaLinks, htmlFinaLinks = await self.paramSpider.getDynamicScriptLinks(session, url, result)
                                if scriptFinaLinks:
                                    for scriptLink in scriptFinaLinks:
                                        if self.domain in scriptLink:
                                            self.linkList.append(scriptLink)
                                if htmlFinaLinks:
                                    for htmlLink in htmlFinaLinks:
                                        if self.domain in htmlLink:
                                            self.linkList.append(htmlLink)
                                print(scriptFinaLinks, htmlFinaLinks)
                            # 探测后台目录
                            # self._getBackend(session, url)
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
            print(e.args)
            print('[-] curl {} error.'.format(url))
        finally:
            self.pbar.update(1)

    async def _getBackend(self, session, url):
        """
        这个想法是看到大师兄代码里面的，然后自己觉得也有必要添加，原因是后台管理
        也算是敏感的资产后面通过WebCrack可以快速的实现相关基于后台的弱口令探测
        """
        for backend in self.backendKeywordList:
            try:
                pass
            except Exception as e:
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

    pbar = tqdm(total=len(['test.com']), desc='[{}]'.format('Test'), ncols=100)
    alive = AliveSpider('bhlqjt.com', ['http://test.shack2.org'], pbar)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(alive.main())
