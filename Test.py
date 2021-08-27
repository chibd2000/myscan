# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 1:14

import asyncio
import time


async def test(queue: asyncio.Queue):
    while 1:
        item = await queue.get()
        await asyncio.sleep(1)
        print(item)
        queue.task_done()


async def main():
    queue = asyncio.Queue(-1)
    for i in range(50):
        await queue.put(i)

    taskList = []
    for i in range(10):
        task = asyncio.create_task(test(queue))
        taskList.append(task)

    await queue.join()

    for k in taskList:
        k.cancel()

    await asyncio.gather(*taskList, return_exceptions=True)


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)
