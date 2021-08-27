# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-27 18:24

import socket
import re


def test(ip, port):
    try:
        s = socket.socket()
        s.settimeout(0.7)
        s.connect((ip, int(port)))
        s.send(b'langzi\r\n')
        SocketRecv = (s.recv(1024))
        s.close()
        for k, v in self.Banner.items():
            for b in v:
                banner = re.search(b, SocketRecv, re.I | re.S)
                if banner:
                    return k.decode()
        return '获取失败'
    except Exception as e:
        # Log('向端口发起连接异常:{}'.format(str(e)))
        return '获取失败'
    finally:
        s.close()
