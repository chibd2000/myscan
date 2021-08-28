# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-28 15:16


from threading import Thread

g_num = 100

def test():
    g_num = 2000


if __name__ == '__main__':
    t = Thread(target=test,)
    t.start()
    t.join()
    print(g_num)