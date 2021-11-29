# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2020-11-23 20:45

from core.setting import HTTP_PROXY
from core.exception.github import GithubPrivilegeError
from core.public import *
from spider import BaseSpider
from spider.common import config


class GithubSpider(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'GithubSpider'  #
        self.domain = domain
        self.per_page = 50
        self.githubApi = config.githubApi
        self.addr = 'https://api.github.com/search/code?s=indexed&type=Code&o=desc&q="{}"&page={}&per_page={}'
        # self.keyword = ['password', 'smtp', 'passwd', 'mail', 'mysql']

    # 这个writeFile保存函数其实是可以进行优化的，后面写完了继续改下，要不然每个Spider保存数据的时候都需要去加上这将近10行的代码
    # 主要的还是对这个要写入Dict中的字段进行遍历解析即可
    def writeFile(self, web_lists, page):
        # 这里的writeFile用于到时候github中敏感信息的保存函数
        pass

    # def process_pages(self, _contents, _keyword):
    #     def get_data(github_file):
    #         if not github_file.last_modified:
    #             try:
    #                 github_file.update()
    #             except UnknownObjectException:
    #                 pass
    #         repo = github_file.repository
    #         return {
    #             'keyword': _keyword,
    #             'sha': github_file.sha,
    #             'fragment': format_fragments(github_file.text_matches),
    #             'html_url': github_file.html_url,
    #             'last_modified': dateutil.parser.parse(
    #                 github_file.last_modified) if github_file.last_modified else None,
    #             'file_name': github_file.name,
    #             'repo_name': repo.name,
    #             'repo_url': repo.html_url,
    #             'user_avatar': repo.owner.avatar_url,
    #             'user_name': repo.owner.login,
    #             'user_url': repo.owner.html_url
    #         }
    #
    #     def format_fragments(_text_matches):
    #         return ''.join([f['fragment'] for f in _text_matches])
    #
    #     for _file in _contents:
    #         print(_file)
    #         data = get_data(_file)
    #         # 这里对数据进行存储
    #         self.resList.append(data)
    #     # get_data(1)

    async def githubSearch(self, session, page):
        # @ske
        # type=c搜索代码，s=indexed排序的类型，o=desc排序方式，page第几页，
        # q=搜索的关键字，q=signtool+sign+pfx+language:Batchfile  指定语言在q参数里，使用language参数
        # extension:pfx 指定后缀在q参数里，使用extension参数
        headers = {"Authorization": 'token {}'.format(self.githubApi)}
        async with session.get(url=self.addr.format(self.domain, page, self.per_page, proxy=HTTP_PROXY),
                               headers=headers, timeout=self.reqTimeout, verify_ssl=False) as response:
            text = await response.json()
            await asyncio.sleep(2)
            if 'API rate limit exceeded' in text:
                print('[-] check your github api rate limit')
                raise GithubPrivilegeError from None
            return text

    async def getSubdomains(self, session, url):
        async with session.get(url=url, headers=self.headers, timeout=self.reqTimeout, verify_ssl=False, proxy=HTTP_PROXY) as response:
            text = await response.text('utf-8', 'ignore')
            subdomains = self.matchSubdomain(self.domain, text)
            self.resList.extend(subdomains)

    async def getSensitiveInfor(self):
        pass

    async def spider(self):
        # # 获取github请求会话
        # session = Github(login_or_token=self.githubApi, per_page=self.page)
        # # 获取请求页数
        # while True:
        #     try:
        #         response = session.search_code('password zjhu.edu.cn', sort='indexed', order='desc', highlight=True)
        #
        #         # github api支持最多搜索1000条记录
        #         total = min(response.totalCount, 1000)
        #         break
        #     except GithubException as e:
        #         if 'rate limit' in e.data.get('message', ''):
        #             print('[-] Github token error, {}'.format(e.__str__()))
        #             return
        #     except ReadTimeoutError:
        #         continue
        #     # 防止由于网络原因导致的获取失败
        #     except Exception as e:
        #         print('[-] Github search error, error is {}'.format(e.__str__()))
        #         return
        taskList = []
        taskRawHtmlList = []
        # get first page
        try:
            async with aiohttp.ClientSession() as session:
                text1 = await self.githubSearch(session, 1)
                total_count = text1['total_count']
                # E.G. total = 50，max_page = 1; total = 51, max_page = 2
                # 需要搜索的页数为max_page和task.page中最小的值
                max_page = (total_count // self.per_page) if (not total_count % self.per_page) else (
                        total_count // self.per_page + 1)
                pages = min(max_page, 300)
                print('[+] github get pages is {}.'.format(pages))
                for page in range(1, pages):  # pages page 20 is test something
                    json_text = await self.githubSearch(session, page)
                    if json_text and 'items' in json_text.keys():
                        items = json_text['items']
                        for item in items:
                            raw_url = item['html_url'].replace('https://github.com/', 'https://raw.githubusercontent.com/').replace('/blob/', '/')
                            taskRawHtmlList.append(raw_url)

                taskRawHtmlList = list(set(taskRawHtmlList))
                for _ in taskRawHtmlList:
                    taskList.append(asyncio.create_task(self.getSubdomains(session, _)))

                # 这里则进行异步操作对每个构造好的raw.githubusercontent.com中的内容进行匹配
                await asyncio.gather(*taskList)  # [[{}],[{}]]
        except GithubPrivilegeError:
            print('[-] curl github.com error, please check your API Limit.'.format(self.source))
            return []
        except aiohttp.ClientHttpProxyError:
            print('[-] curl github.com need outer proxy.'.format(self.source))
            return []
        except Exception as e:
            print('[-] [{}] curl api.github.com error, the erorr is {}'.format(self.source, e.args))
            return []

        self.resList = list(set(self.resList))
        print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))
        return self.resList
        # # 搜索代码
        # page = 0
        # # 获取每页的内容
        # while page < max_page:
        #     try:
        #         page_content = response.get_page(page)
        #         page += 1
        #     except GithubException as e:
        #         print('[-] GithubException, error is {}'.format(e.__str__()))
        #         continue
        #     # 防止由于网络原因导致的获取失败
        #     except Exception as e:
        #         print('[-] Github search error, error is {}'.format(e.__str__()))
        #         return
        #     print(page_content)
        #     self.process_pages(page_content, self.keyword)

        # 这里进行打印即可
        # self.resList = list(set(self.resList))
        # print(self.resList)
        # print('[+] [{}] [{}] {}'.format(self.source, len(self.resList), self.resList))

    async def main(self):
        return await self.spider()


if __name__ == '__main__':
    github = GithubSpider('zjhu.edu.cn')
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(github.main())
