# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2020-11-23 20:45

from core.exception.github import GithubPrivilegeError
from core.data import config_dict, gLogger
from spider import BaseSpider
import aiohttp
import asyncio


class GithubSpider(BaseSpider):
    def __init__(self, domain, name):
        super().__init__()
        self.name = name
        self.source = 'GithubSpider'
        self.domain = domain
        self.per_page = 50
        self.api = config_dict['github']
        self.proxy = config_dict['proxy']
        self.addr = 'https://api.github.com/search/code?s=indexed&type=Code&o=desc&q="{}"&page={}&per_page={}'
        # self.keyword = ['password', 'smtp', 'passwd', 'mail', 'mysql']

    async def github_search(self, session, page):
        # @ske
        # type=c搜索代码，s=indexed排序的类型，o=desc排序方式，page第几页，
        # q=搜索的关键字，q=signtool+sign+pfx+language:Batchfile  指定语言在q参数里，使用language参数
        # extension:pfx 指定后缀在q参数里，使用extension参数
        headers = {'Authorization': 'token {}'.format(self.api)}
        async with session.get(url=self.addr.format(self.domain, page, self.per_page), proxy=self.proxy,
                               headers=headers, timeout=self.reqTimeout, verify_ssl=False) as response:
            text = await response.json()
            await asyncio.sleep(2)
            if 'API rate limit exceeded' in text:
                raise GithubPrivilegeError("github api rate limit") from None
            return text

    async def get_subdomains(self, session, url):
        async with session.get(url=url, headers=self.headers, timeout=self.reqTimeout, verify_ssl=False, proxy=self.proxy) as response:
            text = await response.text('utf-8', 'ignore')
            await asyncio.sleep(2)
            subdomains = self.match_subdomain(self.domain, text)
            self.res_list.extend(subdomains)

    async def getSensitiveInfor(self):
        pass

    async def spider(self):
        task_list = []
        task_raw_html_list = []
        # get first page
        try:
            async with aiohttp.ClientSession() as session:
                text = await self.github_search(session, 1)
                total_count = text['total_count']
                # E.G. total = 50，max_page = 1; total = 51, max_page = 2
                # 需要搜索的页数为max_page和task.page中最小的值
                max_page = (total_count // self.per_page) if (not total_count % self.per_page) else (total_count // self.per_page + 1)
                pages = min(max_page, 300)
                # print('[+] github get pages is {}.'.format(pages))
                for page in range(1, pages):  # pages page 20 is test something
                    json_text = await self.github_search(session, page)
                    if json_text and 'items' in json_text.keys():
                        items = json_text['items']
                        for item in items:
                            raw_url = item['html_url'].replace('https://github.com/','https://raw.githubusercontent.com/').replace('/blob/','/')
                            task_raw_html_list.append(raw_url)
                task_raw_html_list = list(set(task_raw_html_list))
                for _ in task_raw_html_list:
                    task_list.append(asyncio.create_task(self.get_subdomains(session, _)))
                # 这里则进行异步操作对每个构造好的raw.githubusercontent.com中的内容进行匹配
                await asyncio.gather(*task_list)  # [[{}],[{}]]
        except GithubPrivilegeError as e:
            gLogger.myscan_error('curl github.com error, the error is {}'.format(e.message))
            return []
        except aiohttp.ClientHttpProxyError:
            gLogger.myscan_error('curl github.com need outer proxy.')
            return []
        except Exception as e:
            gLogger.myscan_error('curl api.github.com error, the erorr is {}'.format(e.args))
            return []
        self._is_continue = False
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))

    async def main(self):
        await self.spider()
        return self.res_list


if __name__ == '__main__':
    github = GithubSpider('zjhu.edu.cn', 'test')
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(github.main())
