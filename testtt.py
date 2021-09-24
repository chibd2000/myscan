# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-09 13:28
import base64
import urllib

#
# def b64strEncode(input: str):
#     RAW = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
#     CUSTOM = "gx74KW1roM9qwzPFVOBLSlYaeyncdNbI=JfUCQRHtj2+Z05vshXi3GAEuT/m8Dpk6"
#     transformer = input.maketrans(RAW, CUSTOM)
#     return base64.b64encode(input.encode()).decode().translate(transformer)
#
#
# def b64strDecode(input: str):
#     RAW = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
#     CUSTOM = "gx74KW1roM9qwzPFVOBLSlYaeyncdNbI=JfUCQRHtj2+Z05vshXi3GAEuT/m8Dpk6"
#     transformer = input.maketrans(RAW, CUSTOM)
#     return base64.b64decode(input.encode()).decode().translate(transformer)
#

if __name__ == '__main__':
    a = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    b = "gx74KW1roM9qwzPFVOBLSlYaeyncdNbI=JfUCQRHtj2+Z05vshXi3GAEuT/m8Dpk6"
    out = ""

    c = input("\n1.加密  2.解密  0.退出\n\n请选择处理方式：")

    while c != 0:
        out = ""
        if c == 1:
            str = raw_input("\n请输入要处理的字符串：")
            str = base64.b64encode(str)
            for i in str:
                out += b[a.index(i)]
            print("\n处理结果为：" + out)
        elif c == 2:
            str = raw_input("\n请输入要处理的字符串：")
            for i in str:
                out += a[b.index(i)]
            out = base64.b64decode(out)
            print("\n处理结果为：" + out)
        else:
            print("\n输入有误！！只能输入“1”和“2”，请重试！")
        c = input("\n1.加密  2.解密  0.退出\n\n请选择处理方式：")

    # print base64.b64decode(s)