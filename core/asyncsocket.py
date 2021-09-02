# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-27 22:46

import asyncio
import asyncore

import socket


class Client(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))

    def handle_write(self):
        self.send('hello'.encode())

    def handle_read(self):
        print(self.recv(1024).decode('utf-8'))


class AsyncSocketer:
    def test(self):
        pass


# 193.144.76.212:8000
# 150.158.186.39:3443
async def main():
    loop = asyncio.get_event_loop()
    a, b = await loop.create_connection(asyncio.BaseProtocol, host='150.158.186.39', port=3443)
    print(a, b)


if __name__ == '__main__':
    asyncio.run(main())

    # server = Server('localhost', 9090)
    # client = Client('localhost', 9090)
