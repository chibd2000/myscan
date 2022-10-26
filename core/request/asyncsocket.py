# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-27 22:46

import asyncio
import asyncore
import socket

"""
封装用于服务端口利用
"""


class Client(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def handleWrite(self):
        self.send('hello'.encode())

    def handleRead(self):
        print(self.recv(1024).decode('utf-8'))


class AsyncSocketer:
    def test(self):
        pass


async def testecho(message):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 6377)

    print(f'Send: {message!r}')
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()


asyncio.run(testecho('Hello World!'))


# 193.144.76.212:8000
# 150.158.186.39:3443
async def main():
    pass
    # t = Client('127.0.0.1', 6377)
    # t.handle_write()
    # t.handle_read()


if __name__ == '__main__':
    asyncio.run(testecho('aaaaaa'))
