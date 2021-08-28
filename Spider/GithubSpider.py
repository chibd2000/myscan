# coding=utf-8

from spider.BaseSpider import *
from github import Github
from github import GithubException
from spider.common import config

abs_path = os.getcwd() + os.path.sep


class GithubSpider(Spider):
    def __init__(self, domain):
        super().__init__()
        self.source = 'GithubSpider'  #
        self.domain = domain
        self.page = 50
        self.githubApi = config.githubApi
        self.keyword = []

    def writeFile(self, web_lists, page):
        workbook = openpyxl.load_workbook(abs_path + str(random) + ".xlsx")
        worksheet = workbook.worksheets[page]
        index = 0
        while index < len(web_lists):
            web = list()
            web.append(web_lists[index]['spider'])
            web.append(web_lists[index]['keyword'])
            web.append(web_lists[index]['link'])
            web.append(web_lists[index]['title'])
            worksheet.append(web)
            index += 1
        workbook.save(abs_path + str(random) + ".xlsx")
        workbook.close()

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
        session = Github(login_or_token=self.githubApi, per_page=self.page)
        while True:
            try:
                response = session.search_code(self.keyword, sort='indexed', order='desc', highlight=True)
                # github api支持最多搜索1000条记录
                total = min(response.totalCount, 1000)
                break
            except GithubException as e:
                if 'rate limit' in e.data.get('message', ''):
                    print('[-] Github token error, {}', e.args)
                    return
            # 防止由于网络原因导致的获取失败
            except Exception as e:
                print(e.args)
                return
        # E.G. total = 50，max_page = 1; total = 51, max_page = 2
        # 需要搜索的页数为max_page和task.page中最小的值
        max_page = (total // self.page) if (not total % self.page) else (total // self.page + 1)
        pages = min(max_page, self.task.pages) if self.task.pages else max_page
        # 搜索代码
        page = 0
        while page < pages:
            try:
                page_content = response.get_page(page)
                page += 1
            except GithubException as e:
                if 'abuse-rate-limits' in e.data.get('documentation_url'):
                    session, _token = self._reset_token(session, _token)
                else:
                    logger.exception(e)
                continue
            # 防止由于网络原因导致的获取失败
            except Exception as e:
                print(e.args)
                return
            self.process_pages(page_content, self.keyword)

    def main(self):
        logging.info("GithubSpider Start")
        await self.spider()
        return list(set(self.resList))


if __name__ == '__main__':
    pass
