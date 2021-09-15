# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-10 21:02
import base64
from core.MyAsyncHttp import *
from spider.common import config


async def fofaSearch(keyword):
    url = "https://fofa.so/api/v1/search/all?email={}&key={}&qbase64={}&size=10000&fields=host"
    # print(url.format(config.fofaEmail, config.fofaApi, base64.b64encode(keyword.encode()).decode()))
    async with aiohttp.ClientSession() as session:
        jsonResult = await AsyncFetcher.fetch(session=session, url=url.format(config.fofaEmail, config.fofaApi, base64.b64encode(keyword.encode()).decode()), json=True)
        print('[+] fofa get data success.')
        return jsonResult['results']


async def shodanSearch():
    pass


async def quekaSearch():
    pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(fofaSearch('domain="zjhu.edu.cn"'))
    print(result)
