# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-27 22:06

import asyncio
import aiohttp
import random
import hashlib
from typing import Union, Tuple, Any


class AsyncFetcher:

    @staticmethod
    def getUserAgent():
        user_agents = [
            'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0) chromeframe/10.0.648.205',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_0) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.13) Gecko/20101213 Opera/9.80 (Windows NT 6.1; U; zh-tw) Presto/2.7.62 Version/11.01',
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
            'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11',
        ]
        return random.choice(user_agents)

    @staticmethod
    async def fetch(session, url, params=None, json=False, *args, **kwargs) -> Union[str, dict, list]:
        try:
            if params is None:
                async with session.get(url, verify_ssl=False, *args, **kwargs) as response:
                    if response is not None:
                        await asyncio.sleep(2)
                        return await response.text() if json is False else await response.json()
            else:
                async with session.get(url, verify_ssl=False, params=params, *args, **kwargs) as response:
                    if response is not None:
                        await asyncio.sleep(2)
                        return await response.text() if json is False else await response.json()
        except Exception as e:
            return ''

    @staticmethod
    async def post_fetch(session, url, data=None, params=None, json=False, *args, **kwargs):
        try:
            if params is None:
                async with session.post(url=url, verify_ssl=False, data=data, *args, **kwargs) as response:
                    if response is not None:
                        await asyncio.sleep(2)
                        return await response.text() if json is False else await response.json()
            else:
                async with session.post(url=url, verify_ssl=False, data=data, params=params, *args, **kwargs) as response:
                    if response is not None:
                        await asyncio.sleep(2)
                        return await response.text() if json is False else await response.json()
        except Exception:
            return ''

    @staticmethod
    async def get_favicon_md5_fetch(session, url, *args, **kwargs):
        try:
            async with session.get(url, verify_ssl=False, *args, **kwargs) as response:
                if response is not None:
                    await asyncio.sleep(2)
                    text = await response.read()
                    m1 = hashlib.md5()
                    m1.update(text)
                    favicon_md5 = m1.hexdigest()
                    return favicon_md5
        except Exception as e:
            return ''

    @staticmethod
    async def takeover_fetch(session, url, *args, **kwargs) -> Union[Tuple[Any, Any], str]:
        try:
            url = f'http://{url}' if str(url).startswith(('http:', 'https:')) is False else url
            async with session.get(url, verify_ssl=False, *args, **kwargs) as response:
                if response is not None:
                    await asyncio.sleep(2)
                    return url, await response.text()
        except Exception:
            return url, ''

    @classmethod
    async def fetch_all(cls, urls, headers=None, params='', json=False, takeover=False, *args, **kwargs) -> list:
        timeout = aiohttp.ClientTimeout()
        if headers is None:
            headers = {'User-Agent': AsyncFetcher.getUserAgent()}
        if takeover:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                tuples = await asyncio.gather(*[AsyncFetcher.takeover_fetch(session, url, *args, **kwargs) for url in urls])
                return tuples
        if params is None:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                texts = await asyncio.gather(*[AsyncFetcher.fetch(session=session, url=url, json=json, *args, **kwargs) for url in urls])
                return texts
        else:
            async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
                texts = await asyncio.gather(*[AsyncFetcher.fetch(session=session, url=url, params=params, json=json, *args, **kwargs) for url in urls])
                return texts
