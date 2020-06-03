# coding=utf-8

a = 0


def aaa():
    global a
    a += 1
    if a != 10:
        aaa()
    if a == 10:
        return
aaa()

print(a)

print("我已经解析结束了！")