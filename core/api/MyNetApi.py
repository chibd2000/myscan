# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-10 21:02
import base64
from core.request.asynchttp import *
from spider.common import config


async def searchInterface(*args, **kwargs):
    # if kwargs[0] == 'fofa':
    #     fofaSearch()
    pass


async def fofaSearch(keyword):
    url = "https://fofa.so/api/v1/search/all?email={}&key={}&qbase64={}&size=1000&fields=host"
    async with aiohttp.ClientSession() as session:
        result = await AsyncFetcher.fetch(session=session, url=url.format(config.fofaEmail, config.fofaApi,
                                                                          base64.b64encode(keyword.encode()).decode()),
                                          json=True)
        # print(result.get('results'))
        return result.get('results')


async def shodanSearch(keyword):
    url = "https://shodan.io/api/v1/search/all?email={}&key={}&qbase64={}&size=1000&fields=host"
    async with aiohttp.ClientSession() as session:
        result = await AsyncFetcher.fetch(session=session, url=url.format(config.fofaEmail, config.fofaApi,
                                                                          base64.b64encode(keyword.encode()).decode()),
                                          json=True)
        return result.get('results')


async def quekaSearch(keyword):
    url = "https://quake.360.com/api/v1/search/all?email={}&key={}&qbase64={}&size=1000&fields=host"
    async with aiohttp.ClientSession() as session:
        result = await AsyncFetcher.fetch(session=session, url=url.format(config.fofaEmail, config.fofaApi,
                                                                          base64.b64encode(keyword.encode()).decode()),
                                          json=True)
        return result.get('results')


async def hunterSearch(keyword):
    url = "https://hunter.qianxin.com/api/v1/search/all?email={}&key={}&qbase64={}&size=1000&fields=host"
    async with aiohttp.ClientSession() as session:
        result = await AsyncFetcher.fetch(session=session, url=url.format(config.fofaEmail, config.fofaApi,
                                                                          base64.b64encode(keyword.encode()).decode()),
                                          json=True)
        return result.get('results')


async def zoomeyeSearch(keyword):
    url = ''
    pass
    # url -X GET 'https://api.zoomeye.org/host/search?query=hostname%3A%20zjhu.edu.cn&pageSize=200&facets=hostname,ip,port,service,asn' -H "API-KEY:12104626-7ce8-a2c9f-4997-f3ba52738f3"


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(fofaSearch('app="泛微-EMobile" && country="CN"'))
    # result = loop.run_until_complete(shodanSearch('app="yapi"'))
    # result = loop.run_until_complete(quekaSearch('app="yapi"'))
