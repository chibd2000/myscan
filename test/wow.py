# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-10-22 21:07
import aiohttp
import asyncio

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'Cache-Control': 'max-age=0',
    'DNT': '1',
    'Referer': 'https://www.google.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Upgrade-Insecure-Requests': '1',
    'X-Forwarded-For': '127.0.0.1',
    # 'Connection': 'keep-alive'  # 实战中遇到过的BUG，有些站点需要保持KEEP
}


async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://172-18-0-44-8080.webvpn.nbcc.cn', headers=headers) as response:
            if response is not None and response.status == 200:
                text = await response.text()
                print(text)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(test())
    # import requests
    # import random
    # user_agent_list = [
    #     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    # ]
    # headers['User-Agent'] = random.choice(user_agent_list)
    # response = requests.get('https://172-18-0-44-8080.webvpn.nbcc.cn', verify=False, headers=headers)
    # print(response.text)
    # print(response)
