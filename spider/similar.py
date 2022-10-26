# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-26 13:46
from core.utils.differ import DifferentChecker
from spider import BaseSpider


def get_similarity_match(domain, domain_list):
    result_list = []
    new_domain_list = [i for i in domain_list if domain in i]
    domain_index = 0
    while domain_index < len(new_domain_list):
        current = new_domain_list[domain_index]
        good_index_list = DifferentChecker.get_close_match_index(current, new_domain_list, n=10000, cutoff=0.8)
        current_result_list = []
        for index in reversed(sorted(good_index_list)):
            current_result_list.append(new_domain_list[index])
            del new_domain_list[index]
        result_list.append(current_result_list)
        domain_index += 1
    return result_list


class SimilarSpider(BaseSpider):
    def __init__(self, domain, name, domain_list):
        super().__init__()
        self.domain = domain
        self.name = name
        self.source = 'Similar'
        self.res_list = get_similarity_match(domain, domain_list)

    async def spider(self):
        self._is_continue = False
        self.write_file(self.get_unique_list(self.res_list), 16)

    async def main(self):
        await self.spider()


if __name__ == '__main__':
    beian = SimilarSpider('zjhu.edu.cn', '')
    # loop = asyncio.get_event_loop()
    # res = loop.run_until_complete(beian.main())
