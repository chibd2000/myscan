# coding=utf-8
# @Author   : zpchcbd HG team
# @Time     : 2021-08-28 17:47

import requests
import codecs
import hashlib
import mmh3
import aiohttp
from bs4 import BeautifulSoup
import random


class HackRequest(object):
    def __init__(self, domain, cookie=None, hash=None, md5=None):
        self.domain = domain
        self.cookie = cookie
        self.iconHash = hash
        self.iconMD5 = md5
        self._getFaviconAndMD5()

    def _getFaviconAndMD5(self):
        try:
            print(self.getUrl(self.domain) + '/favicon.ico')
            resp = requests.get(self.getUrl(self.domain) + '/favicon.ico')
            m1 = hashlib.md5()
            m1.update(resp.content)
            theMD5 = m1.hexdigest()
            favicon = codecs.encode(resp.content, 'base64')
            self.iconHash = mmh3.hash(favicon)
            self.iconMD5 = theMD5
            print('[+] get iconHash: ', self.iconHash)
            print('[+] get iconMD5: ', self.iconMD5)
        except Exception as e:
            print('[-] _getFaviconAndMD5 first failed, error is {}'.format(e.args))
            print('[+] _getFaviconAndMD5 second ...')
            try:
                resp_ = requests.get(self.getUrl('www.' + self.domain) + '/favicon.ico')
                m1_ = hashlib.md5()
                m1_.update(resp_.content)
                theMD5 = m1_.hexdigest()
                favicon = codecs.encode(resp_.content, 'base64')
                self.iconHash = mmh3.hash(favicon)
                self.iconMD5 = theMD5
                print('[+] get iconHash: ', self.iconHash)
                print('[+] get iconMD5: ', self.iconMD5)
            except Exception as e:
                print('[-] _getFaviconAndMD5 second failed, error is {}'.format(e.args))

    async def getRequest(self, url):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    text = await resp.text()
                    title = self._getTitle(text).strip().replace('\r', '').replace('\n', '')
                    status = resp.status
                    return title, status, resp
        except Exception as e:
            return e

    def _getHeaders(self):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:61.0) '
            'Gecko/20100101 Firefox/68.0',
            'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/68.0']
        ua = random.choice(user_agents)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,'
                      'application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': 'https://www.google.com/',
            'User-Agent': ua,
            'Upgrade-Insecure-Requests': '1',
            'X-Forwarded-For': '127.0.0.1',
        }
        return headers

    def _getTitle(self, markup):
        soup = BeautifulSoup(markup, 'lxml')

        title = soup.title
        if title:
            return title.text

        h1 = soup.h1
        if h1:
            return h1.text

        h2 = soup.h2
        if h2:
            return h2.text

        h3 = soup.h3
        if h2:
            return h3.text

        desc = soup.find('meta', attrs={'name': 'description'})
        if desc:
            return desc['content']

        word = soup.find('meta', attrs={'name': 'keywords'})
        if word:
            return word['content']

        text = soup.text
        if len(text) <= 200:
            return text
        return ''

    def getUrl(self, domain):
        if 'http://' in domain or 'https://' in domain:
            return f'{domain}'
        else:
            if ':443' in domain:
                return f'https://{domain}'

            if ':80' in domain:
                return f'http://{domain}'

            return f'http://{domain}'
