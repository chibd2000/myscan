# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 1:14

import asyncio
import os
import time

# async def test(queue: asyncio.Queue):
#     while 1:
#         item = await queue.get()
#         await asyncio.sleep(1)
#         print(item)
#         queue.task_done()
#
#
# async def main():
#     queue = asyncio.Queue(-1)
#     for i in range(50):
#         await queue.put(i)
#
#     taskList = []
#     for i in range(10):
#         task = asyncio.create_task(test(queue))
#         taskList.append(task)
#
#     await queue.join()
#
#     for k in taskList:
#         k.cancel()
#
#     await asyncio.gather(*taskList, return_exceptions=True)
from urllib.parse import quote

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from core.utils.InformationProvider import InformationProvider


async def _baidu(search, page):
    async with ClientSession() as session:
        for n in range(0, page * 10, 10):
            base_url = 'https://www.baidu.com/s?wd=' + str(quote(search)) + '&oq=' + str(
                quote(search)) + '&ie=utf-8' + '&pn=' + str(n)
            async with session.get(url=base_url) as response:
                if response:
                    res = await response.text()
                    print(res)
                    soup = BeautifulSoup(res, "html.parser")
                    for a in soup.select('div.c-container > h3 > a'):
                        async with session.get(url=a['href']) as response:
                            if response:
                                url = str(response.url)
                                yield url


async def test02():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        await asyncio.sleep(10)

        await asyncio.sleep(5)

        return 1


def test01():
    try:
        a = 1 / 0
    except:
        return 1
    finally:
        print(22)


def test02():
    try:
        print(1 == 1)
    except:
        pass
    finally:
        print(2)
    return 3


async def test():
    async for url in _baidu("inurl:zjhu.edu.cn", 5):
        print(url)


def test0202():
    passwordDict = InformationProvider.readFile(os.path.join(InformationProvider.dictPath, 'redis_passwords.txt'))
    print(list(passwordDict))


def test0303():
    raise ConnectionResetError("aaaaaaaaaaaa")


class A(object):
    def __test(self):
        print('test')

    def test(self):
        self.__test()


if __name__ == '__main__':
    # l = asyncio.get_event_loop()
    # l.run_until_complete(test())
    a = A()

    # start = time.time()
    # asyncio.run(test02())
    # print(time.time() - start)
