# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-27 22:46

import asyncio
from _socket import AF_INET


class AsyncSocketer:
    def test(self):
        pass


# 193.144.76.212:8000
# 150.158.186.39:3443
async def main():
    loop = asyncio.get_event_loop()
    a, b = await loop.create_connection(asyncio.Protocol, host='150.158.186.39', port=3443)
    print(a, b)

if __name__ == '__main__':
    asyncio.run(main())
