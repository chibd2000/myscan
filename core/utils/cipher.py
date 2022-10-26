# coding=utf-8
# @Author   : zpchcbd HG team
# @Blog     : https://www.cnblogs.com/zpchcbd/
# @Time     : 2021-12-06 17:37

from base64 import b64encode, urlsafe_b64encode
import pyDes

"""
比如空间搜索引擎、类似exp读取的敏感信息需要通过解密来记录，所以封装下相关加解密的函数
"""


def encodeCommonBase64(content):
    return b64encode(content.encode()).decode()


def encodeUrlBase64(content):
    return urlsafe_b64encode(content.encode()).decode()


def decodeDes128bit(secret_key, s):
    try:
        cipherX = pyDes.des('        ')  # 默认就需要8位，所以这里就先用空格来进行填充，后面再用解密密钥来进行填充
        cipherX.setKey(secret_key)
        decodeText = cipherX.decrypt(s)
    except Exception:
        decodeText = ''
    return decodeText


def encodeHtml(content):
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    return "<string>" + "".join(html_escape_table.get(c, c) for c in content) + "</string>"


if __name__ == '__main__':
    print(encodeCommonBase64('1234'))
