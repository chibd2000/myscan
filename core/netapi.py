# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-09-10 21:02
import base64

from core.exception.net import NetPageLimitError, NetTokenError
from core.data import config_dict
from core.request.asynchttp import AsyncFetcher
import aiohttp


async def searchInterface(*args, **kwargs):
    # if kwargs[0] == 'fofa':
    #     fofaSearch()
    pass


async def fofaSearch(keyword):
    try:
        fofa_api = config_dict['fofa']['fofa_api']
        fofa_email = config_dict['fofa']['fofa_email']
        url = "https://fofa.info/api/v1/search/all?email={}&key={}&qbase64={}&size=1000&fields=host"
        async with aiohttp.ClientSession() as session:
            ret_json = await AsyncFetcher.fetch(session=session, url=url.format(fofa_email, fofa_api, base64.b64encode(keyword.encode()).decode()), json=True)
            if 'Account Invalid' in str(ret_json):
                raise NetTokenError from None
            if 'restrict access' in str(ret_json):
                raise NetPageLimitError from None
            return ret_json.get('results')
    except NetPageLimitError:
        print('[-] check your fofa search limit.')
        exit(0)
    except NetTokenError:
        print('[-] check your fofa search account.')
        exit(0)


async def shodanSearch(keyword):
    url = "https://shodan.io/api/v1/search/all?email={}&key={}&qbase64={}&size=1000&fields=host"
    async with aiohttp.ClientSession() as session:
        ret_json = await AsyncFetcher.fetch(session=session, url=url.format('fofa_email', 'fofa_api', base64.b64encode(
            keyword.encode()).decode()), json=True)
        return result.get('results')


async def quekaSearch(keyword):
    url = "https://quake.360.com/api/v1/search/all?email={}&key={}&qbase64={}&size=1000&fields=host"
    async with aiohttp.ClientSession() as session:
        ret_json = await AsyncFetcher.fetch(session=session, url=url.format('fofa_email', 'fofa_api', base64.b64encode(
            keyword.encode()).decode()), json=True)
        return result.get('results')


async def hunterSearch(keyword):
    url = "https://hunter.qianxin.com/api/v1/search/all?email={}&key={}&qbase64={}&size=1000&fields=host"
    async with aiohttp.ClientSession() as session:
        ret_json = await AsyncFetcher.fetch(session=session, url=url.format('fofa_email', 'fofa_api', base64.b64encode(
            keyword.encode()).decode()), json=True)
        return result.get('results')


async def zoomeyeSearch(keyword):
    url = "https://hunter.qianxin.com/api/v1/search/all?email={}&key={}&qbase64={}&size=1000&fields=host"
    async with aiohttp.ClientSession() as session:
        ret_json = await AsyncFetcher.fetch(session=session, url=url.format('fofa_email', 'fofa_api', base64.b64encode(
            keyword.encode()).decode()), json=True)
        return result.get('results')

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(fofaSearch('app="泛微-EMobile" && country="CN"'))
    # result = loop.run_until_complete(shodanSearch('app="yapi"'))
    # result = loop.run_until_complete(quekaSearch('app="yapi"'))
