# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-28 0:00

import asyncio


async def test():
    await asyncio.sleep(1)
    return 1


async def main():
    t = await test()
    print(t)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
