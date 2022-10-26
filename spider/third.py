# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-01 22:23

from core.data import path_dict, gLogger
from spider import BaseSpider
import sys
import os
import asyncio
import importlib


class ThirdSpider(BaseSpider):
    def __init__(self, domain, name):
        super().__init__()
        self.source = 'ThirdSpider'
        self.domain = domain
        self.name = name

    async def get_third(self):
        sys.path.append(path_dict.SPIDER_THIRD_PATH)
        third_module_list = filter(lambda x: (True, False)[x[-3:] == 'pyc' or x[-5:] == '__.py' or x[:2] == '__' or x[-3:] == 'log'], os.listdir(path_dict.SPIDER_THIRD_PATH))
        task_list = []
        for _ in third_module_list:
            module = importlib.import_module(_[:-3])
            if hasattr(module, 'do'):
                do_method = getattr(module, 'do')
                task_list.append(asyncio.create_task(do_method(self.domain)))
        result_list = await asyncio.gather(*task_list)
        for _ in result_list:
            self.res_list.extend(_)

    async def spider(self):
        await self.get_third()
        self.res_list = list(set(self.res_list))
        gLogger.myscan_info('[{}] [{}] {}'.format(self.source, len(self.res_list), self.res_list))

    async def main(self):
        await self.spider()
        return self.res_list


if __name__ == '__main__':
    pass
