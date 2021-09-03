# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 1:14

import asyncio
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
import aiohttp


async def test02():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        await asyncio.sleep(10)

        await asyncio.sleep(5)

        return 1

def test01():
    try:
        a = 1/0
    except:
        return 1
    finally:
        print(22)


if __name__ == '__main__':
    b = test01()
    print(b)
    # start = time.time()
    # asyncio.run(test02())
    # print(time.time() - start)
