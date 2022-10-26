# coding=utf-8
from core.data import gLogger
from core.data import path_dict
import re
import openpyxl


class BaseSpider:
    __slots__ = ('source', 'headers', 'reqTimeout', 'domain', 'res_list', 'name', '_is_continue')

    def __init__(self):
        self.name = None
        self.source = 'BaseSpider'
        self._is_continue = True
        self.reqTimeout = 20
        self.res_list = []
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://www.google.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'X-Forwarded-For': '127.0.0.1',
            # 'Connection': 'keep-alive'  # 实战中遇到过的BUG，有些站点需要保持KEEP
        }

    def write_file(self, web_lists, page):
        try:
            workbook = openpyxl.load_workbook(path_dict.ROOT_PATH + str(self.name) + ".xlsx")
            worksheet = workbook.worksheets[page]
            for web_info in web_lists:
                web = []
                for _ in web_info.values():
                    web.append(_)
                worksheet.append(web)
            workbook.save(path_dict.ROOT_PATH + str(self.name) + ".xlsx")
            workbook.close()
        except FileNotFoundError:
            gLogger.myscan_warn('if you want to record search and attack information, you need start with -o param.')
        except Exception as e:
            gLogger.myscan_warn('[{}] write_file error, error is {}'.format(self.source, e.__str__()))

    def spider(self):
        """subclass write"""

    def main(self):
        """subclass write"""

    # 获取 title service
    async def get_title_and_service(self, session, link):
        try:
            async with session.get(url=link, headers=self.headers, verify_ssl=False, timeout=10) as response:
                text = await response.text()
                title = re.findall(r'<title>(.*?)</title>', text, re.S)[0].strip(' ').strip('\r\n').strip('\n').strip('\r')
                service = response.headers.get('Server', '')
            try:
                content = text
            except:
                content = ''
            return title, service, content
        except:
            title = ''
            return title, '', ''

    # 匹配每个页面中的子域名
    def match_subdomain(self, domain, text):
        regexp = r'(?:[a-z0-9](?:[a-z0-9\-]{0,61}[a-z0-9])?\.){0,}' + domain.replace('.', r'\.')
        result = re.findall(regexp, text, flags=re.I | re.S)
        if not result:
            return list()
        deal = map(lambda s: s.lower(), result)
        return list(deal)

    # 列表中的字典 键值重复清理
    def get_unique_list(self, L):
        (output, temp) = ([], [])
        for l in L:
            for k, v in l.items():
                flag = False
                if (k, v) not in temp:
                    flag = True
                    break
            if flag:
                output.append(l)
            temp.extend(l.items())
        return output