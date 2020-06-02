# coding=utf-8

from multiprocessing import Pool
from Spider.PortSpider import *


class bbbbb(object):

    def __init__(self, num):
        self.num = num

    def test11(self):
        print(1)

    def testsss(self):
        self.test11()


if __name__ == '__main__':
    p = Pool(2)
    clear_task_list = [
        {'subdomain': 'vpn.xxxx.cn', 'ips': '42.112.33.25', 'port': None, 'target': 'subdomain'},
        {'subdomain': 'www.xxxx.cn', 'ips': '183.221.237.217', 'port': None, 'target': 'subdomain'}
    ]


    # clear_task_list = [1, 2, 3, 4, 5]
    for i in clear_task_list:
        aaaaaaa = bbbbb('ncist.cn')
        p.apply_async(func=aaaaaaa.test11)

    p.close()
    p.join()






