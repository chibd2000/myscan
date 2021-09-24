# coding=utf-8

from spider.public import *
from spider import BaseSpider
from github import Github, UnknownObjectException
from github import GithubException
from spider.common import config
import logging


class GithubSpider(BaseSpider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'GithubSpider'  #
        self.domain = domain
        self.page = 50
        self.githubApi = config.githubApi
        self.keyword = []

    def writeFile(self, web_lists, page):
        pass

    def process_pages(self, _contents, _keyword):

        def get_data(github_file):
            if not github_file.last_modified:
                try:
                    github_file.update()
                except UnknownObjectException:
                    pass
            repo = github_file.repository
            return {
                'keyword': _keyword,
                'sha': github_file.sha,
                'fragment': format_fragments(github_file.text_matches),
                'html_url': github_file.html_url,
                'last_modified': dateutil.parser.parse(
                    github_file.last_modified) if github_file.last_modified else None,
                'file_name': github_file.name,
                'repo_name': repo.name,
                'repo_url': repo.html_url,
                'user_avatar': repo.owner.avatar_url,
                'user_name': repo.owner.login,
                'user_url': repo.owner.html_url
            }

    def spider(self):
        # 获取github请求会话
        session = Github(login_or_token=self.githubApi, per_page=self.page)
        # 获取请求页数
        while True:
            try:
                response = session.search_code(self.keyword, sort='indexed', order='desc', highlight=True)
                # github api支持最多搜索1000条记录
                total = min(response.totalCount, 1000)
                break
            except GithubException as e:
                if 'rate limit' in e.data.get('message', ''):
                    print('[-] Github token error, {}'.format(e.__str__()))
                    return
            # 防止由于网络原因导致的获取失败
            except Exception as e:
                print('[-] Github search error, error is {}'.format(e.__str__()))
                return

        # E.G. total = 50，max_page = 1; total = 51, max_page = 2
        # 需要搜索的页数为max_page和task.page中最小的值
        max_page = (total // self.page) if (not total % self.page) else (total // self.page + 1)
        # 搜索代码
        page = 0
        # 获取每页的内容
        while page < max_page:
            try:
                page_content = response.get_page(page)
                page += 1
            except GithubException as e:
                # print('[-] GithubException, error is {}'.format(e.__str__()))
                continue
            # 防止由于网络原因导致的获取失败
            except Exception as e:
                print('[-] Github search error, error is {}'.format(e.__str__()))
                return
            self.process_pages(page_content, self.keyword)

    async def main(self):
        await self.spider()
        return list(set(self.resList))


if __name__ == '__main__':
    pass
