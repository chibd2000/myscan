# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-31 14:40

import asyncio
import aiodns
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

loop = asyncio.get_event_loop()
resolver = aiodns.DNSResolver(loop=loop)


async def query(name, query_type):
    return await resolver.query(name, query_type)


coro = query('google.com', 'A')
result = loop.run_until_complete(coro)
print(result[0].host)
